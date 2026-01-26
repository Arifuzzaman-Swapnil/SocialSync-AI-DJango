# C:\Users\Trust computer\Desktop\Final_version_socialSync\analytics\models.py

from django.db import models
from django.contrib.auth.models import User
from posts.models import Post

class Analytics(models.Model):
    """Track engagement metrics for posts"""
    
    METRIC_TYPES = [
        ('likes', 'Likes'),
        ('shares', 'Shares'),
        ('comments', 'Comments'),
        ('views', 'Views'),
        ('clicks', 'Clicks'),
        ('impressions', 'Impressions'),
        ('engagement_rate', 'Engagement Rate'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='analytics', null=True, blank=True)
    platform = models.CharField(max_length=20)
    
    # Metrics
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    metric_value = models.IntegerField(default=0)
    
    # Timestamps
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics'
        verbose_name = 'Analytics'
        verbose_name_plural = 'Analytics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['post', 'platform']),
        ]
    
    def __str__(self):
        post_info = f"Post {self.post.id}" if self.post else "Overall"
        return f"{self.user.username} - {self.platform} - {self.metric_type}: {self.metric_value} ({post_info})"