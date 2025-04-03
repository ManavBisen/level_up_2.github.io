from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from datetime import timedelta
import os

class LevelTitle(models.Model):
    level = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Level {self.level}: {self.title}"
    
    class Meta:
        ordering = ['level']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)  # Current XP towards next level
    total_xp = models.IntegerField(default=0)  # Total XP accumulated
    title = models.CharField(max_length=100, default='None')
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        try:
            if self.image and os.path.exists(self.image.path):
                img = Image.open(self.image.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
        except (FileNotFoundError, ValueError, OSError):
            # If the image file doesn't exist or has other issues, skip processing
            pass
    
    def get_xp_for_next_level(self):
        # Calculate XP needed to level up (10 + level, max 60)
        return min(10 + self.level, 60)
    
    def add_xp(self, amount):
        """Add XP to the user and handle level-ups"""
        if amount <= 0:
            return
        
        self.xp += amount
        self.total_xp += amount
        
        # Check for level up
        notifications_to_create = []
        while self.xp >= self.get_xp_for_next_level():
            self.xp -= self.get_xp_for_next_level()
            self.level += 1
            
            # Update title based on level
            self._update_title()
            
            # Store notification to create (we'll batch create them later)
            notifications_to_create.append(
                Notification(
                    user=self.user,
                    message=f"Congratulations! You've reached level {self.level}!"
                )
            )
        
        # Update the database directly without triggering signals again
        Profile.objects.filter(pk=self.pk).update(
            xp=self.xp,
            total_xp=self.total_xp,
            level=self.level,
            title=self.title
        )
        
        # Create the batched notifications
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
    
    def _update_title(self):
        """Update the user's title based on their level"""
        # Try to find a title for the current level
        level_title = LevelTitle.objects.filter(level__lte=self.level).order_by('-level').first()
        if level_title:
            self.title = level_title.title
        else:
            # If no title found, use default titles
            if self.level == 0:
                self.title = 'None'
            elif self.level == 1:
                self.title = 'Beginner'
            elif self.level >= 5 and self.level < 10:
                self.title = 'Player'
            elif self.level >= 10 and self.level < 20:
                self.title = 'Bounty 1Thousand'
            elif self.level >= 20:
                self.title = 'Bounty 100Thousand'
    
    def remove_xp(self, amount):
        """Remove XP (for punishments)"""
        if amount <= 0:
            return
        
        # Can't go below 0 total XP
        amount = min(amount, self.total_xp)
        
        self.total_xp -= amount
        
        # Check if we need to drop levels
        notifications_to_create = []
        while self.xp < 0:
            if self.level <= 0:
                # Can't go below level 0
                self.xp = 0
                break
                
            # Drop a level
            self.level -= 1
            self.xp += self.get_xp_for_next_level()
            self._update_title()
            
            # Store notification to create
            notifications_to_create.append(
                Notification(
                    user=self.user,
                    message=f"Oh no! You've dropped to level {self.level}."
                )
            )
        
        # Update the database directly without triggering signals again
        Profile.objects.filter(pk=self.pk).update(
            xp=self.xp,
            total_xp=self.total_xp,
            level=self.level,
            title=self.title
        )
        
        # Create the batched notifications
        if notifications_to_create:
            Notification.objects.bulk_create(notifications_to_create)
    
    def get_rank(self):
        """Get the user's rank based on total XP"""
        higher_xp_count = Profile.objects.filter(total_xp__gt=self.total_xp).count()
        return higher_xp_count + 1

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."
    
    @classmethod
    def cleanup_old_notifications(cls, days=1):
        """Delete notifications older than specified days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_notifications = cls.objects.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()
        return count

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username} sent {self.amount} XP to {self.receiver.username}"
