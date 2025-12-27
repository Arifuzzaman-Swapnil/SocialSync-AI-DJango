"""
Messenger Bot Views
Handles Facebook Messenger connection, PDF uploads, and configuration
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

from .models import (
    MessengerConnection, 
    AIConfiguration, 
    PDFKnowledgeBase,
    CustomPrompt,
    Conversation,
    Message
)
from .forms import (
    MessengerConnectionForm,
    AIConfigurationForm,
    CustomPromptForm,
    PDFUploadForm
)

logger = logging.getLogger(__name__)


@login_required
def connect_messenger(request):
    """Main connection page for Facebook Messenger"""
    
    # Check if user already has a connection
    try:
        connection = MessengerConnection.objects.get(user=request.user)
        # Redirect to dashboard if already connected
        return redirect('messenger_dashboard')
    except MessengerConnection.DoesNotExist:
        connection = None
    
    if request.method == 'POST':
        connection_form = MessengerConnectionForm(request.POST)
        ai_form = AIConfigurationForm(request.POST)
        prompt_form = CustomPromptForm(request.POST)
        pdf_form = PDFUploadForm(request.POST, request.FILES)
        
        if connection_form.is_valid() and ai_form.is_valid() and prompt_form.is_valid():
            try:
                # Create connection
                connection = connection_form.save(commit=False)
                connection.user = request.user
                connection.save()
                
                # Create AI configuration
                ai_config = ai_form.save(commit=False)
                ai_config.connection = connection
                ai_config.save()
                
                # Create custom prompt
                prompt = prompt_form.save(commit=False)
                prompt.connection = connection
                prompt.save()
                
                # Handle PDF uploads
                if pdf_form.is_valid():
                    pdf_files = request.FILES.getlist('pdfs')
                    for pdf_file in pdf_files:
                        PDFKnowledgeBase.objects.create(
                            connection=connection,
                            file=pdf_file,
                            filename=pdf_file.name,
                            file_size=pdf_file.size,
                            status='pending'
                        )
                
                messages.success(
                    request, 
                    f'🎉 Successfully connected {connection.page_name}! Your chatbot is ready.'
                )
                return redirect('messenger_success')
                
            except Exception as e:
                logger.error(f"Error creating messenger connection: {e}")
                messages.error(
                    request, 
                    f'Error connecting messenger: {str(e)}'
                )
        else:
            # Show form errors
            for form in [connection_form, ai_form, prompt_form, pdf_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    
    else:
        # Initial forms
        connection_form = MessengerConnectionForm()
        ai_form = AIConfigurationForm()
        prompt_form = CustomPromptForm()
        pdf_form = PDFUploadForm()
    
    context = {
        'connection_form': connection_form,
        'ai_form': ai_form,
        'prompt_form': prompt_form,
        'pdf_form': pdf_form,
    }
    
    return render(request, 'messenger_bot/connect.html', context)


@login_required
def messenger_success(request):
    """Success page after connection"""
    
    try:
        connection = MessengerConnection.objects.get(user=request.user)
    except MessengerConnection.DoesNotExist:
        messages.error(request, 'No messenger connection found.')
        return redirect('connect_messenger')
    
    context = {
        'connection': connection,
        'webhook_url': request.build_absolute_uri(f'/messenger/webhook/{connection.page_id}/'),
        'verify_token': connection.verify_token,
    }
    
    return render(request, 'messenger_bot/success.html', context)


@login_required
def messenger_dashboard(request):
    """Dashboard showing all conversations and messages"""
    
    try:
        connection = MessengerConnection.objects.get(user=request.user)
    except MessengerConnection.DoesNotExist:
        messages.warning(request, 'Please connect your Messenger page first.')
        return redirect('connect_messenger')
    
    # Get all conversations
    conversations = Conversation.objects.filter(
        connection=connection
    ).order_by('-last_message_at')
    
    # Get selected conversation
    conversation_id = request.GET.get('conversation')
    selected_conversation = None
    messages_list = []
    
    if conversation_id:
        selected_conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            connection=connection
        )
        messages_list = Message.objects.filter(
            conversation=selected_conversation
        ).order_by('timestamp')
    
    context = {
        'connection': connection,
        'conversations': conversations,
        'selected_conversation': selected_conversation,
        'messages': messages_list,
    }
    
    return render(request, 'messenger_bot/dashboard.html', context)


@login_required
def messenger_settings(request):
    """Settings page for managing connection and AI config"""
    
    try:
        connection = MessengerConnection.objects.get(user=request.user)
        ai_config = connection.ai_config
    except MessengerConnection.DoesNotExist:
        messages.warning(request, 'Please connect your Messenger page first.')
        return redirect('connect_messenger')
    except AIConfiguration.DoesNotExist:
        messages.error(request, 'AI configuration not found.')
        return redirect('messenger_dashboard')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'connection':
            form = MessengerConnectionForm(request.POST, instance=connection)
            if form.is_valid():
                form.save()
                messages.success(request, '✅ Connection settings updated!')
                return redirect('messenger_settings')
        
        elif form_type == 'ai_config':
            form = AIConfigurationForm(request.POST, instance=ai_config)
            if form.is_valid():
                form.save()
                messages.success(request, '✅ AI configuration updated!')
                return redirect('messenger_settings')
        
        elif form_type == 'new_prompt':
            form = CustomPromptForm(request.POST)
            if form.is_valid():
                prompt = form.save(commit=False)
                prompt.connection = connection
                prompt.save()
                messages.success(request, '✅ Custom prompt created!')
                return redirect('messenger_settings')
    
    # Get forms
    connection_form = MessengerConnectionForm(instance=connection)
    ai_form = AIConfigurationForm(instance=ai_config)
    prompt_form = CustomPromptForm()
    
    # Get existing prompts
    prompts = CustomPrompt.objects.filter(connection=connection)
    
    # Get uploaded PDFs
    pdfs = PDFKnowledgeBase.objects.filter(connection=connection)
    
    context = {
        'connection': connection,
        'connection_form': connection_form,
        'ai_form': ai_form,
        'prompt_form': prompt_form,
        'prompts': prompts,
        'pdfs': pdfs,
    }
    
    return render(request, 'messenger_bot/settings.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request, page_id):
    """
    Facebook Messenger webhook endpoint
    Handles verification and incoming messages
    """
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe':
            try:
                connection = MessengerConnection.objects.get(page_id=page_id)
                
                if token == connection.verify_token:
                    # Mark webhook as verified
                    connection.is_webhook_verified = True
                    connection.save()
                    
                    logger.info(f"Webhook verified for page {page_id}")
                    return JsonResponse({'challenge': int(challenge)}, safe=False)
                else:
                    logger.warning(f"Invalid verify token for page {page_id}")
                    return JsonResponse({'error': 'Invalid verify token'}, status=403)
            
            except MessengerConnection.DoesNotExist:
                logger.error(f"Connection not found for page {page_id}")
                return JsonResponse({'error': 'Connection not found'}, status=404)
        
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = json.loads(request.body)
            
            # Log incoming webhook data
            logger.info(f"Received webhook data: {data}")
            
            # Process webhook data here
            # This will be implemented in next steps with RAG
            
            return JsonResponse({'status': 'received'}, status=200)
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def disconnect_messenger(request):
    """Disconnect Messenger page"""
    
    if request.method == 'POST':
        try:
            connection = MessengerConnection.objects.get(user=request.user)
            page_name = connection.page_name
            connection.delete()
            
            messages.success(
                request, 
                f'✅ Successfully disconnected {page_name}'
            )
        except MessengerConnection.DoesNotExist:
            messages.error(request, 'No connection found to disconnect.')
    
    return redirect('connect_accounts')


@login_required
def upload_pdf(request):
    """Upload additional PDFs to knowledge base"""
    
    try:
        connection = MessengerConnection.objects.get(user=request.user)
    except MessengerConnection.DoesNotExist:
        return JsonResponse({'error': 'No connection found'}, status=404)
    
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            pdf_files = request.FILES.getlist('pdfs')
            uploaded_count = 0
            
            for pdf_file in pdf_files:
                PDFKnowledgeBase.objects.create(
                    connection=connection,
                    file=pdf_file,
                    filename=pdf_file.name,
                    file_size=pdf_file.size,
                    status='pending'
                )
                uploaded_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Uploaded {uploaded_count} PDF(s)',
                'count': uploaded_count
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_pdf(request, pdf_id):
    """Delete a PDF from knowledge base"""
    
    if request.method == 'POST':
        try:
            connection = MessengerConnection.objects.get(user=request.user)
            pdf = get_object_or_404(
                PDFKnowledgeBase, 
                id=pdf_id, 
                connection=connection
            )
            
            filename = pdf.filename
            pdf.file.delete()  # Delete actual file
            pdf.delete()  # Delete database record
            
            messages.success(request, f'✅ Deleted {filename}')
            return JsonResponse({'success': True})
        
        except MessengerConnection.DoesNotExist:
            return JsonResponse({'error': 'No connection found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)