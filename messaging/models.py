from django.db import models
from django.contrib.auth.models import User
import os

def message_file_path(instance, filename):
    """Generate file path for message attachments"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Set new filename with message id
    filename = f'message_{instance.id}.{ext}'
    # Return full path
    return os.path.join('message_attachments', filename)

def audio_file_path(instance, filename):
    """Generate file path for audio message attachments"""
    # Audio files will always be .webm
    filename = f'audio_{instance.id}.webm'
    # Return full path
    return os.path.join('audio_messages', filename)

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)  # Allow blank for audio-only messages
    file = models.FileField(upload_to=message_file_path, null=True, blank=True)
    audio = models.FileField(upload_to=audio_file_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:30]}..."
    
    @classmethod
    def get_conversation(cls, user1, user2):
        """Get all messages between two users"""
        return cls.objects.filter(
            (models.Q(sender=user1) & models.Q(receiver=user2)) |
            (models.Q(sender=user2) & models.Q(receiver=user1))
        ).order_by('timestamp')
    
    @classmethod
    def get_conversations(cls, user):
        """Get all users that the given user has conversations with"""
        # Get all users the current user has sent messages to
        sent_to = cls.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
        
        # Get all users the current user has received messages from
        received_from = cls.objects.filter(receiver=user).values_list('sender', flat=True).distinct()
        
        # Combine the two lists and remove duplicates
        user_ids = set(list(sent_to) + list(received_from))
        
        # Get the User objects
        users = User.objects.filter(id__in=user_ids)
        
        return users

class CommunityMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_messages')
    content = models.TextField(blank=True)  # Allow blank for audio-only messages
    file = models.FileField(upload_to=message_file_path, null=True, blank=True)
    audio = models.FileField(upload_to=audio_file_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Community message from {self.sender.username}: {self.content[:30]}..."
