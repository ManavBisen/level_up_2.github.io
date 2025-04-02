from django.contrib import admin
from .models import Profile, Notification, UserLevel, Title

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'total_xp', 'current_xp', 'title')
    search_fields = ('user__username', 'title__name')
    list_filter = ('level', 'title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'created_at', 'is_read')
    search_fields = ('recipient__username', 'message')
    list_filter = ('is_read', 'created_at')

@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'xp_required')
    list_filter = ('level',)

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_level', 'description')
    search_fields = ('name', 'description')
    list_filter = ('required_level',)
