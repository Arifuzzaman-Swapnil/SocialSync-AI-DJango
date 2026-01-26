# ai_image/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
import uuid
import base64


def logo_upload_path(instance, filename):
    """Generate unique path for uploaded logos"""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return f"user_logos/{instance.user.id}/{new_filename}"


def generated_image_path(instance, filename):
    """Generate unique path for generated images"""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return f"generated_images/{instance.user.id}/{new_filename}"


class UserImageSettings(models.Model):
    """Store user's API keys and settings for image generation"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='image_settings')
    
    # Encrypted API key storage (simple base64 encoding)
    _gemini_api_key = models.TextField(blank=True, null=True, db_column='gemini_api_key')
    
    # Default settings
    default_style = models.CharField(max_length=50, default='realistic', choices=[
        ('realistic', 'Realistic'),
        ('artistic', 'Artistic'),
        ('anime', 'Anime/Manga'),
        ('cartoon', 'Cartoon'),
        ('3d_render', '3D Render'),
        ('watercolor', 'Watercolor'),
        ('oil_painting', 'Oil Painting'),
        ('digital_art', 'Digital Art'),
        ('pixel_art', 'Pixel Art'),
        ('sketch', 'Sketch/Drawing'),
    ])
    
    default_size = models.CharField(max_length=20, default='1024x1024', choices=[
        ('512x512', '512x512 (Small)'),
        ('768x768', '768x768 (Medium)'),
        ('1024x1024', '1024x1024 (Large)'),
        ('1024x576', '1024x576 (Landscape)'),
        ('576x1024', '576x1024 (Portrait)'),
        ('1920x1080', '1920x1080 (Full HD)'),
    ])
    
    # Usage tracking
    total_images_generated = models.IntegerField(default=0)
    total_api_calls = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Image Settings"
        verbose_name_plural = "User Image Settings"
    
    def __str__(self):
        return f"Image Settings - {self.user.username}"
    
    def set_gemini_api_key(self, api_key):
        """Encode and store the API key"""
        if api_key:
            encoded = base64.b64encode(api_key.encode()).decode()
            self._gemini_api_key = encoded
        else:
            self._gemini_api_key = None
    
    def get_gemini_api_key(self):
        """Decode and return the API key"""
        if self._gemini_api_key:
            try:
                decoded = base64.b64decode(self._gemini_api_key.encode()).decode()
                return decoded
            except Exception:
                return None
        return None
    
    @property
    def has_api_key(self):
        """Check if user has set an API key"""
        return bool(self._gemini_api_key)
    
    @property
    def masked_api_key(self):
        """Return masked version of API key for display"""
        key = self.get_gemini_api_key()
        if key and len(key) > 8:
            return f"{key[:6]}...{key[-4:]}"
        return None


class UserLogo(models.Model):
    """Store user's uploaded logos"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logos')
    name = models.CharField(max_length=100)
    logo_file = models.ImageField(upload_to=logo_upload_path)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # If this logo is set as default, unset others
        if self.is_default:
            UserLogo.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ImageGeneration(models.Model):
    """Store generated images history"""
    
    STYLE_CHOICES = [
        ('realistic', 'Realistic'),
        ('artistic', 'Artistic'),
        ('anime', 'Anime/Manga'),
        ('cartoon', 'Cartoon'),
        ('3d_render', '3D Render'),
        ('watercolor', 'Watercolor'),
        ('oil_painting', 'Oil Painting'),
        ('digital_art', 'Digital Art'),
        ('pixel_art', 'Pixel Art'),
        ('sketch', 'Sketch/Drawing'),
        ('cinematic', 'Cinematic'),
        ('fantasy', 'Fantasy'),
        ('minimalist', 'Minimalist'),
        ('vintage', 'Vintage/Retro'),
        ('neon', 'Neon/Cyberpunk'),
    ]
    
    SIZE_CHOICES = [
        ('512x512', '512x512'),
        ('768x768', '768x768'),
        ('1024x1024', '1024x1024'),
        ('1024x576', '1024x576 (Landscape)'),
        ('576x1024', '576x1024 (Portrait)'),
        ('1920x1080', '1920x1080 (Full HD)'),
        ('1080x1920', '1080x1920 (Story)'),
    ]
    
    LOGO_POSITION_CHOICES = [
        ('none', 'No Logo'),
        ('top_left', 'Top Left'),
        ('top_right', 'Top Right'),
        ('top_center', 'Top Center'),
        ('bottom_left', 'Bottom Left'),
        ('bottom_right', 'Bottom Right'),
        ('bottom_center', 'Bottom Center'),
        ('center', 'Center'),
    ]
    
    QUALITY_CHOICES = [
        ('standard', 'Standard'),
        ('high', 'High Quality'),
        ('ultra', 'Ultra HD'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_generations')
    
    # Input
    title = models.CharField(max_length=200, help_text="Title for the image")
    prompt = models.TextField(help_text="Detailed description for image generation")
    negative_prompt = models.TextField(blank=True, null=True, help_text="What to avoid in the image")
    
    # Style Settings
    style = models.CharField(max_length=30, choices=STYLE_CHOICES, default='realistic')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='1024x1024')
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='high')
    
    # Logo Settings
    logo = models.ForeignKey(UserLogo, on_delete=models.SET_NULL, null=True, blank=True)
    logo_position = models.CharField(max_length=20, choices=LOGO_POSITION_CHOICES, default='none')
    logo_size = models.IntegerField(default=10, help_text="Logo size as percentage of image (5-30)")
    logo_opacity = models.IntegerField(default=100, help_text="Logo opacity (10-100)")
    
    # Advanced Options
    seed = models.IntegerField(blank=True, null=True, help_text="Seed for reproducibility")
    enhance_prompt = models.BooleanField(default=True, help_text="AI-enhance the prompt")
    add_lighting = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('', 'Default'),
        ('natural', 'Natural Light'),
        ('studio', 'Studio Lighting'),
        ('dramatic', 'Dramatic'),
        ('soft', 'Soft/Diffused'),
        ('golden_hour', 'Golden Hour'),
        ('neon', 'Neon Lights'),
        ('backlit', 'Backlit'),
    ])
    camera_angle = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('', 'Default'),
        ('front', 'Front View'),
        ('side', 'Side View'),
        ('aerial', 'Aerial/Bird\'s Eye'),
        ('low_angle', 'Low Angle'),
        ('high_angle', 'High Angle'),
        ('closeup', 'Close-up'),
        ('wide', 'Wide Shot'),
        ('macro', 'Macro'),
    ])
    
    # Output
    generated_image = models.ImageField(upload_to=generated_image_path, blank=True, null=True)
    generated_image_with_logo = models.ImageField(upload_to=generated_image_path, blank=True, null=True)
    enhanced_prompt = models.TextField(blank=True, null=True, help_text="AI-enhanced prompt used")
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(default=0, help_text="Processing time in seconds")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Image Generation"
        verbose_name_plural = "Image Generations"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_display_image(self):
        """Return image with logo if available, otherwise original"""
        if self.generated_image_with_logo:
            return self.generated_image_with_logo
        return self.generated_image
    
    def get_size_tuple(self):
        """Return size as tuple (width, height)"""
        parts = self.size.split('x')
        return (int(parts[0]), int(parts[1]))


class SavedImage(models.Model):
    """User's saved/favorite images"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_images')
    image_generation = models.ForeignKey(ImageGeneration, on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    image_file = models.ImageField(upload_to=generated_image_path)
    prompt = models.TextField(blank=True, null=True)
    
    is_favorite = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class PromptTemplate(models.Model):
    """Pre-defined prompt templates for image generation"""
    
    CATEGORY_CHOICES = [
        ('social_media', 'Social Media'),
        ('marketing', 'Marketing'),
        ('product', 'Product'),
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape'),
        ('abstract', 'Abstract'),
        ('logo_design', 'Logo Design'),
        ('banner', 'Banner/Header'),
        ('illustration', 'Illustration'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_templates', null=True, blank=True)
    is_global = models.BooleanField(default=False, help_text="Available to all users")
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    prompt_template = models.TextField(help_text="Use {subject}, {style}, {color} as placeholders")
    negative_prompt = models.TextField(blank=True, null=True)
    recommended_style = models.CharField(max_length=30, choices=ImageGeneration.STYLE_CHOICES, default='realistic')
    recommended_size = models.CharField(max_length=20, choices=ImageGeneration.SIZE_CHOICES, default='1024x1024')
    
    preview_image = models.ImageField(upload_to='prompt_templates/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
