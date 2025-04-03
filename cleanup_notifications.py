import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamify.settings')
django.setup()

from users.models import Notification

def cleanup_notifications():
    """Delete notifications older than 1 day"""
    # Delete notifications older than 1 day
    deleted_count = Notification.cleanup_old_notifications(days=1)
    print(f'Successfully deleted {deleted_count} old notifications')
    return deleted_count

if __name__ == '__main__':
    cleanup_notifications()
