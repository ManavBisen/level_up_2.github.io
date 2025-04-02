def notification_processor(request):
    """Context processor to add unread notification count to all templates"""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}
