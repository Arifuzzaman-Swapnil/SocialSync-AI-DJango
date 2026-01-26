# ai_image/views.py

import os
import io
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.core.files.base import ContentFile

from .models import (
    UserImageSettings, UserLogo, ImageGeneration, 
    SavedImage, PromptTemplate
)
from .gemini_service import GeminiImageService


def get_user_api_key(user):
    """Get user's Gemini API key if set"""
    try:
        img_settings = user.image_settings
        return img_settings.get_gemini_api_key()
    except UserImageSettings.DoesNotExist:
        return None


def get_or_create_image_settings(user):
    """Get or create image settings for user"""
    img_settings, created = UserImageSettings.objects.get_or_create(user=user)
    return img_settings


# ============== API Settings ==============

@login_required
def api_settings(request):
    """Manage user's Gemini API settings"""
    
    img_settings = get_or_create_image_settings(request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_key':
            api_key = request.POST.get('gemini_api_key', '').strip()
            if api_key:
                img_settings.set_gemini_api_key(api_key)
                img_settings.save()
                messages.success(request, 'API key saved successfully!')
            else:
                messages.error(request, 'Please enter an API key')
        
        elif action == 'update_defaults':
            img_settings.default_style = request.POST.get('default_style', 'realistic')
            img_settings.default_size = request.POST.get('default_size', '1024x1024')
            img_settings.save()
            messages.success(request, 'Default settings updated!')
        
        elif action == 'delete_key':
            img_settings.set_gemini_api_key(None)
            img_settings.save()
            messages.success(request, 'API key deleted successfully!')
        
        elif action == 'test_key':
            api_key = img_settings.get_gemini_api_key()
            if api_key:
                service = GeminiImageService(api_key=api_key)
                result = service.test_api_key()
                if result['success']:
                    messages.success(request, 'API key is working! ✓')
                else:
                    messages.error(request, f'API key test failed: {result.get("error", "Unknown error")}')
            else:
                messages.error(request, 'No API key set')
        
        return redirect('ai_image:api_settings')
    
    context = {
        'img_settings': img_settings,
    }
    
    return render(request, 'ai_image/api_settings.html', context)


# ============== Logo Management ==============

@login_required
def manage_logos(request):
    """Manage user's logos"""
    
    logos = UserLogo.objects.filter(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'upload':
            name = request.POST.get('name', 'My Logo')
            logo_file = request.FILES.get('logo_file')
            is_default = request.POST.get('is_default') == 'true'
            
            if logo_file:
                # Validate file type
                allowed_types = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
                if logo_file.content_type in allowed_types:
                    UserLogo.objects.create(
                        user=request.user,
                        name=name,
                        logo_file=logo_file,
                        is_default=is_default
                    )
                    messages.success(request, 'Logo uploaded successfully!')
                else:
                    messages.error(request, 'Invalid file type. Please upload PNG, JPEG, GIF, or WebP.')
            else:
                messages.error(request, 'Please select a file to upload.')
        
        elif action == 'set_default':
            logo_id = request.POST.get('logo_id')
            logo = get_object_or_404(UserLogo, pk=logo_id, user=request.user)
            UserLogo.objects.filter(user=request.user).update(is_default=False)
            logo.is_default = True
            logo.save()
            messages.success(request, f'"{logo.name}" set as default logo.')
        
        elif action == 'delete':
            logo_id = request.POST.get('logo_id')
            logo = get_object_or_404(UserLogo, pk=logo_id, user=request.user)
            logo.delete()
            messages.success(request, 'Logo deleted successfully.')
        
        return redirect('ai_image:manage_logos')
    
    context = {
        'logos': logos,
    }
    
    return render(request, 'ai_image/manage_logos.html', context)


@login_required
@require_POST
def upload_logo_ajax(request):
    """AJAX endpoint for logo upload"""
    
    name = request.POST.get('name', 'My Logo')
    logo_file = request.FILES.get('logo_file')
    
    if not logo_file:
        return JsonResponse({'success': False, 'error': 'No file provided'})
    
    allowed_types = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']
    if logo_file.content_type not in allowed_types:
        return JsonResponse({'success': False, 'error': 'Invalid file type'})
    
    logo = UserLogo.objects.create(
        user=request.user,
        name=name,
        logo_file=logo_file,
        is_default=False
    )
    
    return JsonResponse({
        'success': True,
        'logo': {
            'id': logo.pk,
            'name': logo.name,
            'url': logo.logo_file.url,
        }
    })


@login_required
@require_POST
def delete_logo(request, pk):
    """Delete a logo"""
    
    logo = get_object_or_404(UserLogo, pk=pk, user=request.user)
    logo.delete()
    
    return JsonResponse({'success': True, 'message': 'Logo deleted'})


# ============== Image Generator ==============

@login_required
def image_generator(request):
    """Main image generator page"""
    
    img_settings = get_or_create_image_settings(request.user)
    has_api_key = img_settings.has_api_key
    
    # Get user's logos
    logos = UserLogo.objects.filter(user=request.user)
    default_logo = logos.filter(is_default=True).first()
    
    # Get recent generations
    recent_generations = ImageGeneration.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at')[:8]
    
    # Get prompt templates
    templates = PromptTemplate.objects.filter(is_global=True)[:6]
    
    context = {
        'has_api_key': has_api_key,
        'img_settings': img_settings,
        'logos': logos,
        'default_logo': default_logo,
        'recent_generations': recent_generations,
        'templates': templates,
        'style_choices': ImageGeneration.STYLE_CHOICES,
        'size_choices': ImageGeneration.SIZE_CHOICES,
        'quality_choices': ImageGeneration.QUALITY_CHOICES,
        'position_choices': ImageGeneration.LOGO_POSITION_CHOICES,
    }
    
    return render(request, 'ai_image/generator.html', context)


@login_required
@require_POST
def generate_image_ajax(request):
    """AJAX endpoint for image generation"""
    
    try:
        # Check API key
        img_settings = get_or_create_image_settings(request.user)
        if not img_settings.has_api_key:
            return JsonResponse({
                'success': False,
                'error': 'Please set your Gemini API key first.',
                'redirect': '/ai-image/settings/'
            })
        
        # Get form data
        title = request.POST.get('title', 'Untitled Image')
        prompt = request.POST.get('prompt', '')
        negative_prompt = request.POST.get('negative_prompt', '')
        style = request.POST.get('style', 'realistic')
        size = request.POST.get('size', '1024x1024')
        quality = request.POST.get('quality', 'high')
        
        # Logo settings
        logo_id = request.POST.get('logo_id')
        logo_position = request.POST.get('logo_position', 'none')
        logo_size = int(request.POST.get('logo_size', 10))
        logo_opacity = int(request.POST.get('logo_opacity', 100))
        
        # Advanced settings
        lighting = request.POST.get('lighting', '')
        camera_angle = request.POST.get('camera_angle', '')
        enhance_prompt = request.POST.get('enhance_prompt', 'true') == 'true'
        seed = request.POST.get('seed')
        seed = int(seed) if seed else None
        
        if not prompt:
            return JsonResponse({'success': False, 'error': 'Please provide a prompt.'})
        
        # Get logo if specified
        logo = None
        if logo_id and logo_position != 'none':
            try:
                logo = UserLogo.objects.get(pk=logo_id, user=request.user)
            except UserLogo.DoesNotExist:
                pass
        
        # Create generation record
        generation = ImageGeneration.objects.create(
            user=request.user,
            title=title,
            prompt=prompt,
            negative_prompt=negative_prompt,
            style=style,
            size=size,
            quality=quality,
            logo=logo,
            logo_position=logo_position,
            logo_size=logo_size,
            logo_opacity=logo_opacity,
            add_lighting=lighting,
            camera_angle=camera_angle,
            enhance_prompt=enhance_prompt,
            seed=seed,
            status='processing'
        )
        
        # Generate image
        api_key = img_settings.get_gemini_api_key()
        service = GeminiImageService(api_key=api_key)
        
        result = service.generate_image(
            prompt=prompt,
            style=style,
            size=size,
            quality=quality,
            negative_prompt=negative_prompt,
            lighting=lighting,
            camera_angle=camera_angle,
            enhance=enhance_prompt,
            seed=seed
        )
        
        if result['success']:
            # Save generated image
            image_data = result['image_data']
            filename = f"{uuid.uuid4().hex}.png"
            generation.generated_image.save(filename, ContentFile(image_data))
            
            # Add logo if specified
            if logo and logo_position != 'none':
                image_with_logo = service.add_logo_to_image(
                    image_data=image_data,
                    logo_path=logo.logo_file.path,
                    position=logo_position,
                    size_percent=logo_size,
                    opacity=logo_opacity
                )
                logo_filename = f"{uuid.uuid4().hex}_logo.png"
                generation.generated_image_with_logo.save(logo_filename, ContentFile(image_with_logo))
            
            generation.enhanced_prompt = result.get('enhanced_prompt', '')
            generation.processing_time = result.get('processing_time', 0)
            generation.status = 'completed'
            generation.save()
            
            # Update usage stats
            img_settings.total_images_generated += 1
            img_settings.total_api_calls += 1
            img_settings.save()
            
            return JsonResponse({
                'success': True,
                'generation_id': generation.pk,
                'image_url': generation.get_display_image().url if generation.get_display_image() else None,
                'original_url': generation.generated_image.url if generation.generated_image else None,
                'enhanced_prompt': generation.enhanced_prompt,
                'processing_time': round(generation.processing_time, 2)
            })
        else:
            generation.status = 'failed'
            generation.error_message = result.get('error', 'Unknown error')
            generation.save()
            
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to generate image')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def image_result(request, pk):
    """View generated image result"""
    
    generation = get_object_or_404(ImageGeneration, pk=pk, user=request.user)
    
    context = {
        'generation': generation,
    }
    
    return render(request, 'ai_image/result.html', context)


@login_required
def download_image(request, pk):
    """Download generated image"""
    
    generation = get_object_or_404(ImageGeneration, pk=pk, user=request.user)
    
    # Choose image with logo if available
    image_field = generation.get_display_image()
    
    if not image_field:
        return HttpResponse("Image not found", status=404)
    
    # Read image file
    with open(image_field.path, 'rb') as f:
        image_data = f.read()
    
    # Create response
    response = HttpResponse(image_data, content_type='image/png')
    filename = f"{generation.title.replace(' ', '_')}_{generation.pk}.png"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# ============== History & Saved ==============

@login_required
def generation_history(request):
    """View generation history"""
    
    generations = ImageGeneration.objects.filter(user=request.user)
    
    # Filters
    status = request.GET.get('status')
    style = request.GET.get('style')
    
    if status:
        generations = generations.filter(status=status)
    if style:
        generations = generations.filter(style=style)
    
    # Pagination
    paginator = Paginator(generations, 20)
    page = request.GET.get('page')
    generations = paginator.get_page(page)
    
    context = {
        'generations': generations,
        'status_filter': status,
        'style_filter': style,
        'style_choices': ImageGeneration.STYLE_CHOICES,
    }
    
    return render(request, 'ai_image/history.html', context)


@login_required
def saved_images(request):
    """View saved images"""
    
    saved = SavedImage.objects.filter(user=request.user)
    
    # Filter favorites
    favorites_only = request.GET.get('favorites') == 'true'
    if favorites_only:
        saved = saved.filter(is_favorite=True)
    
    # Pagination
    paginator = Paginator(saved, 20)
    page = request.GET.get('page')
    saved = paginator.get_page(page)
    
    context = {
        'saved_images': saved,
        'favorites_only': favorites_only,
    }
    
    return render(request, 'ai_image/saved.html', context)


@login_required
@require_POST
def save_image(request):
    """Save an image to collection"""
    
    generation_id = request.POST.get('generation_id')
    
    generation = get_object_or_404(ImageGeneration, pk=generation_id, user=request.user)
    
    # Check if already saved
    if SavedImage.objects.filter(user=request.user, image_generation=generation).exists():
        return JsonResponse({'success': False, 'error': 'Image already saved'})
    
    # Create saved image
    saved = SavedImage.objects.create(
        user=request.user,
        image_generation=generation,
        title=generation.title,
        image_file=generation.get_display_image(),
        prompt=generation.prompt,
        is_favorite=False
    )
    
    return JsonResponse({
        'success': True,
        'saved_id': saved.pk,
        'message': 'Image saved!'
    })


@login_required
@require_POST
def toggle_favorite_image(request, pk):
    """Toggle favorite status"""
    
    saved = get_object_or_404(SavedImage, pk=pk, user=request.user)
    saved.is_favorite = not saved.is_favorite
    saved.save()
    
    return JsonResponse({
        'success': True,
        'is_favorite': saved.is_favorite
    })


@login_required
@require_POST
def delete_generation(request, pk):
    """Delete a generation"""
    
    generation = get_object_or_404(ImageGeneration, pk=pk, user=request.user)
    
    # Delete associated files
    if generation.generated_image:
        if os.path.exists(generation.generated_image.path):
            os.remove(generation.generated_image.path)
    if generation.generated_image_with_logo:
        if os.path.exists(generation.generated_image_with_logo.path):
            os.remove(generation.generated_image_with_logo.path)
    
    generation.delete()
    
    return JsonResponse({'success': True, 'message': 'Deleted successfully'})


@login_required
@require_POST
def delete_saved_image(request, pk):
    """Delete a saved image"""
    
    saved = get_object_or_404(SavedImage, pk=pk, user=request.user)
    saved.delete()
    
    return JsonResponse({'success': True, 'message': 'Deleted successfully'})


# ============== Templates ==============

@login_required
def prompt_templates(request):
    """View prompt templates"""
    
    global_templates = PromptTemplate.objects.filter(is_global=True)
    user_templates = PromptTemplate.objects.filter(user=request.user)
    
    context = {
        'global_templates': global_templates,
        'user_templates': user_templates,
    }
    
    return render(request, 'ai_image/templates.html', context)


@login_required
@require_POST
def use_template(request, pk):
    """Use a prompt template"""
    
    template = get_object_or_404(PromptTemplate, pk=pk)
    
    # Check access
    if not template.is_global and template.user != request.user:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get variables from request
    variables = {}
    for key in ['subject', 'style', 'color', 'mood', 'setting']:
        if request.POST.get(key):
            variables[key] = request.POST.get(key)
    
    # Fill template
    filled_prompt = template.prompt_template
    for key, value in variables.items():
        filled_prompt = filled_prompt.replace(f'{{{key}}}', value)
    
    return JsonResponse({
        'success': True,
        'prompt': filled_prompt,
        'negative_prompt': template.negative_prompt or '',
        'style': template.recommended_style,
        'size': template.recommended_size,
    })
