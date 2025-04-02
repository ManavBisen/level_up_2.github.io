import os
import django
from users.models import Notification
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamify.settings')
django.setup()

def cleanup_notifications():
    """Delete notifications older than 1 day"""
    # Calculate the cutoff date (1 day ago)
    cutoff_date = timezone.now() - timedelta(days=1)
    
    # Find and delete old notifications
    deleted_count = Notification.objects.filter(created_at__lt=cutoff_date).count()
    Notification.objects.filter(created_at__lt=cutoff_date).delete()
    
    print(f'Successfully deleted {deleted_count} old notifications')
    return deleted_count

if __name__ == '__main__':
    cleanup_notifications()
