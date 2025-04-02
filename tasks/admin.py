from django.contrib import admin
from .models import DailyTask, ExtraTask, GoodWorkSession

@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'completed')
    list_filter = ('date', 'completed')
    search_fields = ('title', 'user__username')

@admin.register(ExtraTask)
class ExtraTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'xp_reward', 'assigned_to', 'completed')
    list_filter = ('completed', 'created_at')
    search_fields = ('title', 'description', 'assigned_to__username')

@admin.register(GoodWorkSession)
class GoodWorkSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'duration_minutes', 'xp_earned')
    list_filter = ('start_time', 'user')
    search_fields = ('user__username',)
