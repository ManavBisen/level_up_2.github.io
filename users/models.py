from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone
from datetime import timedelta
import os


class Title(models.Model):
    name = models.CharField(max_length=100)
    required_level = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (Level {self.required_level})"


class UserLevel(models.Model):
    level = models.PositiveIntegerField(unique=True)
    xp_required = models.PositiveIntegerField()

    def __str__(self):
        return f"Level {self.level} - {self.xp_required} XP required"

    @classmethod
    def get_xp_required(cls, level):
        """
        Calculate XP required to reach the next level.
        Level 0 -> 1: 10 XP
        Level 1 -> 2: 11 XP
        ...
        After level 50, fixed at 60 XP
        """
        try:
            level_obj = cls.objects.get(level=level)
            return level_obj.xp_required
        except cls.DoesNotExist:
            if level < 50:
                return 10 + level
            else:
                return 60


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    level = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    current_xp = models.PositiveIntegerField(default=0)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=100, blank=True)  # For XP transactions

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def add_xp(self, amount):
        """Add XP and handle level up logic"""
        self.total_xp += amount
        self.current_xp += amount

        # Check if user leveled up
        xp_required = UserLevel.get_xp_required(self.level)
        
        while self.current_xp >= xp_required:
            self.current_xp -= xp_required
            self.level += 1
            
            # Check for title update
            self.update_title()
            
            # Get XP required for next level
            xp_required = UserLevel.get_xp_required(self.level)
        
        self.save()
        return self.level

    def subtract_xp(self, amount):
        """Subtract XP and handle level down logic if needed"""
        # Ensure we don't go below 0 total XP
        amount = min(amount, self.total_xp)
        
        self.total_xp -= amount
        
        # Adjust current XP and level
        previous_level = self.level
        self.current_xp -= amount
        
        while self.current_xp < 0 and self.level > 0:
            self.level -= 1
            xp_required = UserLevel.get_xp_required(self.level)
            self.current_xp += xp_required
            
        # If level went below 0, reset to 0
        if self.current_xp < 0:
            self.current_xp = 0
            
        # Update title if level changed
        if previous_level != self.level:
            self.update_title()
            
        self.save()
        return self.level

    def update_title(self):
        """Update user's title based on their level"""
        titles = Title.objects.filter(required_level__lte=self.level).order_by('-required_level')
        
        if titles.exists():
            self.title = titles.first()
        else:
            none_title, created = Title.objects.get_or_create(
                name="None", 
                required_level=0,
                defaults={'description': 'No title yet'}
            )
            self.title = none_title


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}"

    @classmethod
    def cleanup_old_notifications(cls, days=1):
        """Delete notifications older than the specified number of days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_notifications = cls.objects.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()
        return count


class UserSearch(models.Model):
    """Model to track user searches"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} searched for '{self.query}'"
