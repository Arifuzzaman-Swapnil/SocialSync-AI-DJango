# C:\Users\Trust computer\Desktop\Final_version_socialSync\accounts\admin.py

from django.contrib import admin
from .models import UserProfile
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'description']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def value_preview(self, obj):
        """Show preview of value"""
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Value'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_approved', 'subscription_plan', 'posts_this_month', 'created_at']
    list_filter = ['is_approved', 'subscription_plan']
    search_fields = ['user__username', 'user__email', 'company']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'is_approved', 'phone', 'company', 'avatar')
        }),
        ('Subscription', {
            'fields': ('subscription_plan', 'max_social_accounts', 'max_posts_per_month', 'posts_this_month')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )