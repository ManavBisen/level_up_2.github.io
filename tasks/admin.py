from django.contrib import admin
from .models import DailyTask, TaskCompletion, TimerSession, ExtraTask

@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'xp_reward', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name', 'description')

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'task__name')

@admin.register(TimerSession)
class TimerSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'duration_minutes', 'xp_earned')
    list_filter = ('start_time',)
    search_fields = ('user__username',)

@admin.register(ExtraTask)
class ExtraTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'xp_reward', 'assigned_by', 'target_user', 'is_global')
    list_filter = ('is_global',)
    search_fields = ('name', 'description', 'assigned_by__username', 'target_user__username')
