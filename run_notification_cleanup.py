import os
import django
import time
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('notification_cleanup.log')
    ]
)
logger = logging.getLogger('notification_cleanup')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamify.settings')
django.setup()

from users.models import Notification

def cleanup_notifications_job():
    """Run cleanup function for notifications older than 1 day"""
    try:
        deleted_count = Notification.cleanup_old_notifications(days=1)
        logger.info(f'Successfully deleted {deleted_count} old notifications')
        return deleted_count
    except Exception as e:
        logger.error(f'Error cleaning up notifications: {str(e)}')
        return 0

def main():
    """Main function to run cleanup job on a schedule"""
    logger.info("Starting notification cleanup scheduler")
    
    while True:
        # Run the cleanup job
        logger.info("Running notification cleanup job")
        cleanup_notifications_job()
        
        # Sleep for 24 hours (86400 seconds) before running again
        # In production this would be managed by a proper scheduler like celery
        logger.info("Cleanup job completed, sleeping for 24 hours")
        time.sleep(86400)

if __name__ == '__main__':
    main()
