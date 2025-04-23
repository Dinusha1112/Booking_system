"""
URL configuration for bookingsystem project.

Routes URLs to views using path() and include().
For more info: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from booking_system import views


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # App routes
    path('booking', include('booking_system.urls')),  # Main app routes
    path('', views.home, name='home'),
    path('accounts/', include('users.urls')),
    path('users/', include('users.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
