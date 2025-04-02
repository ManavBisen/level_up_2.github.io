from django.contrib import admin
from .models import DirectMessage, CommunityMessage


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'content_preview')
    search_fields = ('sender__username', 'recipient__username', 'content')
    list_filter = ('timestamp',)
    
    def content_preview(self, obj):
        """Show first 50 characters of the message content"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Message'


@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'timestamp', 'content_preview')
    search_fields = ('sender__username', 'content')
    list_filter = ('timestamp',)
    
    def content_preview(self, obj):
        """Show first 50 characters of the message content"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    content_preview.short_description = 'Message'
