from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.connect_account, name='connect_account'),
    path('disconnect/<int:account_id>/', views.disconnect_account, name='disconnect_account'),
]