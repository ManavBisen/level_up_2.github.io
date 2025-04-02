import os
import django
import time
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamify.settings')
django.setup()

from users.models import Notification

def run_cleanup_daemon():
    """
    Runs as a background process to periodically clean up old notifications.
    This script can be set up as a service on the server to run continuously.
    """
    print(f"Starting notification cleanup daemon at {datetime.now()}")
    
    while True:
        try:
            # Delete notifications older than 1 day
            deleted_count = Notification.cleanup_old_notifications(days=1)
            print(f"{datetime.now()} - Cleaned up {deleted_count} old notifications")
            
            # Sleep for 24 hours (86400 seconds)
            # In production, you might want to run this once a day
            time.sleep(86400)
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Sleep for 1 hour and try again
            time.sleep(3600)

if __name__ == '__main__':
    run_cleanup_daemon()
