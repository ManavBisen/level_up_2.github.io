from django.db import models
from django.contrib.auth.models import User
from users.models import Notification


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create notification for new messages
        if is_new:
            Notification.objects.create(
                recipient=self.recipient,
                sender=self.sender,
                message=f"New message from {self.sender.username}"
            )


class CommunityMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='community_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Community message from {self.sender.username}"
