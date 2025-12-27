"""
URL configuration for socialsync project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.shortcuts import render  # ← এটা add করুন

# Placeholder function
def messenger_connect_placeholder(request):
    return render(request, 'messenger_placeholder.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('platforms/', include('platforms.urls')),
    path('posts/', include('posts.urls')),  # এই line add করুন
    path('', include('accounts.urls')),
    path('', lambda request: redirect('login')),
    path('features/', include('upcoming_features.urls')),

    path('messenger/connect/', messenger_connect_placeholder, name='messenger_connect'),
    path('messenger/', include('messenger_bot.urls')),  # ← ADD THIS

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)