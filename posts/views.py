from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Post
from platforms.models import SocialAccount
import json
from datetime import datetime

@login_required
def create_post(request):
    """Create new post"""
    
    # Get user's connected accounts
    connected_accounts = SocialAccount.objects.filter(
        user=request.user, 
        is_active=True
    )
    
    # Group by platform
    platforms = {}
    for account in connected_accounts:
        if account.platform not in platforms:
            platforms[account.platform] = []
        platforms[account.platform].append(account)
    
    if request.method == 'POST':
        # DEBUG: Print all POST data
        print("=" * 50)
        print("POST DATA RECEIVED:")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("=" * 50)
        
        caption = request.POST.get('caption', '').strip()
        scheduled_time = request.POST.get('scheduled_time', '').strip()
        selected_platforms = request.POST.getlist('platforms')
        ai_generated = request.POST.get('ai_generated') == 'true'
        
        # DEBUG: Print extracted values
        print(f"Caption: {caption}")
        print(f"Scheduled Time: {scheduled_time}")
        print(f"Platforms: {selected_platforms}")
        print(f"AI Generated: {ai_generated}")
        
        # Validation
        if not caption:
            print("ERROR: Caption is empty")
            messages.error(request, '❌ Caption is required')
            return redirect('create_post')
        
        if not selected_platforms:
            print("ERROR: No platforms selected")
            messages.error(request, '❌ Please select at least one platform')
            return redirect('create_post')
        
        if not scheduled_time:
            print("ERROR: No scheduled time")
            messages.error(request, '❌ Scheduled time is required')
            return redirect('create_post')
        
# Parse scheduled time
        try:
            import pytz
            
            # Handle both formats
            if 'T' in scheduled_time:
                scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
            else:
                scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
            
            # User's timezone (Bangladesh)
            bd_tz = pytz.timezone('Asia/Dhaka')
            
            # Make aware in Bangladesh timezone
            scheduled_dt = bd_tz.localize(scheduled_dt)
            
            # Convert to UTC (this is what gets saved to database)
            scheduled_dt = scheduled_dt.astimezone(pytz.UTC)
            
            print(f"User input: {scheduled_time}")
            print(f"Saved as UTC: {scheduled_dt}")
                
        except ValueError as e:
            print(f"ERROR: Date parsing failed: {e}")
            messages.error(request, f'❌ Invalid date/time format: {str(e)}')
            return redirect('create_post')
        
        # Check monthly limit
        profile = request.user.profile
        if profile.posts_this_month >= profile.max_posts_per_month:
            print("ERROR: Monthly limit reached")
            messages.error(request, f'❌ Monthly limit reached ({profile.max_posts_per_month} posts)')
            return redirect('create_post')
        
        # Handle media upload
        uploaded_files = request.FILES.getlist('media')  # Changed to getlist
        media_files = []
        if 'media' in request.FILES:
            media_file = request.FILES['media']
            # Save media file
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import os
            
            # Create unique filename
            ext = os.path.splitext(media_file.name)[1]
            filename = f"posts/{request.user.id}/{timezone.now().timestamp()}{ext}"
            
            # Save file
            path = default_storage.save(filename, ContentFile(media_file.read()))
            media_files.append(path)
            print(f"Media saved: {path}")
        
        # Create post
        try:
            print("Creating post...")
            post = Post.objects.create(
                user=request.user,
                caption=caption,
                scheduled_time=scheduled_dt,
                ai_generated=ai_generated,
                status='scheduled'
            )
            
            print(f"Post created with ID: {post.id}")
            
            # Set platforms
            post.set_platforms(selected_platforms)
            print(f"Platforms set: {selected_platforms}")
            
            # Set media files
            if media_files:
                post.set_media_files(media_files)
                print(f"Media files set: {media_files}")
            
            post.save()
            print("Post saved successfully!")
            
            # Update monthly counter
            profile.posts_this_month += 1
            profile.save()
            print(f"Monthly counter updated: {profile.posts_this_month}")
            
            messages.success(request, f'✅ Post scheduled for {scheduled_dt.strftime("%B %d, %Y at %I:%M %p")}')
            print("SUCCESS: Redirecting to my_posts")
            return redirect('my_posts')
            
        except Exception as e:
            print(f"EXCEPTION during post creation: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'❌ Failed to create post: {str(e)}')
            return redirect('create_post')
    
    context = {
        'connected_accounts': connected_accounts,
        'platforms': platforms,
        'has_accounts': connected_accounts.exists(),
    }
    
    return render(request, 'posts/create_post.html', context)

@login_required
def my_posts(request):
    """View user's posts"""
    
    # Get filter
    status_filter = request.GET.get('status', 'all')
    
    # Base query
    posts = Post.objects.filter(user=request.user)
    
    # Apply filter
    if status_filter != 'all':
        posts = posts.filter(status=status_filter)
    
    # Order by scheduled time
    posts = posts.order_by('-scheduled_time')
    
    # Stats
    total_posts = Post.objects.filter(user=request.user).count()
    scheduled_posts = Post.objects.filter(user=request.user, status='scheduled').count()
    posted_posts = Post.objects.filter(user=request.user, status='posted').count()
    failed_posts = Post.objects.filter(user=request.user, status='failed').count()
    
    context = {
        'posts': posts,
        'status_filter': status_filter,
        'total_posts': total_posts,
        'scheduled_posts': scheduled_posts,
        'posted_posts': posted_posts,
        'failed_posts': failed_posts,
    }
    
    return render(request, 'posts/my_posts.html', context)


@login_required
def edit_post(request, post_id):
    """Edit post"""
    
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    # Check if post can be edited
    if not post.can_be_edited():
        messages.error(request, '❌ This post cannot be edited')
        return redirect('my_posts')
    
    if request.method == 'POST':
        caption = request.POST.get('caption', '').strip()
        scheduled_time = request.POST.get('scheduled_time', '').strip()
        selected_platforms = request.POST.getlist('platforms')
        
        # Update post
        post.caption = caption
        post.set_platforms(selected_platforms)
        
        # Parse scheduled time WITH TIMEZONE CONVERSION
        try:
            if 'T' in scheduled_time:
                scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
            else:
                scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
            
            # Bangladesh timezone conversion
            bd_tz = pytz.timezone('Asia/Dhaka')
            scheduled_dt = bd_tz.localize(scheduled_dt)
            
            # Convert to UTC for database
            post.scheduled_time = scheduled_dt.astimezone(pytz.UTC)
            
            print(f"Edit: User input (BD): {scheduled_time}")
            print(f"Edit: Saved as (UTC): {post.scheduled_time}")
            
        except ValueError as e:
            print(f"Edit: Date parsing error: {e}")
            messages.error(request, '❌ Invalid date/time format')
            return redirect('edit_post', post_id=post_id)
        
        post.save()
        
        messages.success(request, '✅ Post updated successfully')
        return redirect('my_posts')
    
    # Get connected accounts
    connected_accounts = SocialAccount.objects.filter(
        user=request.user, 
        is_active=True
    )
    
    # Convert scheduled time to Bangladesh time for display
    bd_tz = pytz.timezone('Asia/Dhaka')
    scheduled_bd = post.scheduled_time.astimezone(bd_tz)
    
    context = {
        'post': post,
        'connected_accounts': connected_accounts,
        'selected_platforms': post.platforms_list,
        'scheduled_time_local': scheduled_bd.strftime('%Y-%m-%dT%H:%M'),
    }
    
    return render(request, 'posts/edit_post.html', context)

@login_required
def delete_post(request, post_id):
    """Delete post"""
    
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == 'POST':
        # Decrease monthly counter if scheduled
        if post.status == 'scheduled':
            profile = request.user.profile
            profile.posts_this_month = max(0, profile.posts_this_month - 1)
            profile.save()
        
        post.delete()
        messages.success(request, '✅ Post deleted successfully')
    
    return redirect('my_posts')


@login_required
def cancel_post(request, post_id):
    """Cancel scheduled post"""
    
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if not post.can_be_cancelled():
        messages.error(request, '❌ This post cannot be cancelled')
        return redirect('my_posts')
    
    if request.method == 'POST':
        post.status = 'cancelled'
        post.save()
        
        messages.success(request, '✅ Post cancelled')
    
    return redirect('my_posts')


@login_required
def generate_caption(request):
    """Generate AI caption"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '').strip()
            tone = data.get('tone', 'professional')
            length = data.get('length', 'medium')
            
            if not topic:
                return JsonResponse({
                    'success': False,
                    'error': 'Topic is required'
                })
            
            # Generate caption using AI
            from ai_caption.services import generate_ai_caption
            
            caption = generate_ai_caption(topic, tone, length)
            
            return JsonResponse({
                'success': True,
                'caption': caption
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })