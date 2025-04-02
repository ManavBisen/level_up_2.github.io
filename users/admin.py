from django.contrib import admin
from .models import Profile, Notification, Transaction, LevelTitle

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp', 'total_xp', 'title')
    list_filter = ('level', 'title')
    search_fields = ('user__username', 'title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username')

@admin.register(LevelTitle)
class LevelTitleAdmin(admin.ModelAdmin):
    list_display = ('level', 'title')
    list_filter = ('level',)
    search_fields = ('title',)
