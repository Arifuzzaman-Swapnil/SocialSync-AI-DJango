"""
Messenger Bot URLs
URL routing for messenger bot functionality
"""

from django.urls import path
from . import views

app_name = 'messenger_bot'

urlpatterns = [
    # Connection
    path('connect/', views.connect_messenger, name='connect'),
    path('success/', views.messenger_success, name='success'),
    path('disconnect/', views.disconnect_messenger, name='disconnect'),
    
    # Dashboard
    path('dashboard/', views.messenger_dashboard, name='dashboard'),
    path('settings/', views.messenger_settings, name='settings'),
    
    # PDF Management
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('delete-pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    
    # Webhook
    path('webhook/<str:page_id>/', views.webhook, name='webhook'),
]