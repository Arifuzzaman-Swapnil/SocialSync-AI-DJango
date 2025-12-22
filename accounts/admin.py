from django.contrib import admin
from .models import UserProfile

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