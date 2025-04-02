import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamify.settings')
django.setup()

from users.models import Notification

def cleanup_notifications():
    """Delete notifications older than 1 day"""
    # Calculate the cutoff date (1 day ago)
    cutoff_date = timezone.now() - timedelta(days=1)
    
    # Find old notifications
    old_notifications = Notification.objects.filter(created_at__lt=cutoff_date)
    count = old_notifications.count()
    
    # Delete them
    old_notifications.delete()
    
    print(f'Successfully deleted {count} old notifications')
    return count

if __name__ == '__main__':
    cleanup_notifications()
