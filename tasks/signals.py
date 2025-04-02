from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DailyTask, TimerSession

@receiver(post_save, sender=TimerSession)
def check_good_work_task_completion(sender, instance, created, **kwargs):
    """Check if the Good Work task is completed when a timer session is saved"""
    if not created and instance.end_time and instance.duration_minutes >= 40:
        try:
            # This is moved to the end_session method in the TimerSession model
            pass
        except DailyTask.DoesNotExist:
            pass
