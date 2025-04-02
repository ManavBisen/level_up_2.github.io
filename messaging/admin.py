from django.contrib import admin
from .models import DirectMessage, CommunityMessage

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'content_preview')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username', 'content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'

@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'timestamp', 'content_preview')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'
