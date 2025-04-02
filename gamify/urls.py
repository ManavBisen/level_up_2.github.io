"""
URL configuration for gamify project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('shop/', include('shop.urls')),
    path('chat/', include('chat.urls')),
    path('bank/', include('bank.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
