"""
URL Configuration for gamify project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home, register, profile, profile_update

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('profile/update/', profile_update, name='profile-update'),
    path('users/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('shop/', include('shop.urls')),
    path('messaging/', include('messaging.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
