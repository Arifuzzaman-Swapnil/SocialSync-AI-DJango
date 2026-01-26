# ai_image/urls.py

from django.urls import path
from . import views

app_name = 'ai_image'

urlpatterns = [
    # Main generator page
    path('', views.image_generator, name='generator'),
    
    # API Settings
    path('settings/', views.api_settings, name='api_settings'),
    
    # Logo Management
    path('logos/', views.manage_logos, name='manage_logos'),
    path('logos/upload/', views.upload_logo_ajax, name='upload_logo'),
    path('logos/delete/<int:pk>/', views.delete_logo, name='delete_logo'),
    
    # Generation
    path('generate/', views.generate_image_ajax, name='generate'),
    path('result/<int:pk>/', views.image_result, name='result'),
    path('download/<int:pk>/', views.download_image, name='download'),
    
    # History
    path('history/', views.generation_history, name='history'),
    path('delete/<int:pk>/', views.delete_generation, name='delete'),
    
    # Saved Images
    path('saved/', views.saved_images, name='saved'),
    path('save/', views.save_image, name='save'),
    path('saved/favorite/<int:pk>/', views.toggle_favorite_image, name='toggle_favorite'),
    path('saved/delete/<int:pk>/', views.delete_saved_image, name='delete_saved'),
    
    # Templates
    path('templates/', views.prompt_templates, name='templates'),
    path('templates/use/<int:pk>/', views.use_template, name='use_template'),
]
