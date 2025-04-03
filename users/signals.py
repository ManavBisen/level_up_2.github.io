from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, LevelTitle

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create Profile when new User is created"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save Profile when User is saved"""
    instance.profile.save()

@receiver(post_save, sender=Profile)
def update_title_based_on_level(sender, instance, created, **kwargs):
    """Update user title when their profile is saved"""
    if not created and not getattr(instance, '_updating_title', False):  # Only run for existing profiles and prevent recursion
        instance._updating_title = True  # Flag to prevent recursion
        instance._update_title()
        # Update the database directly without triggering signals again
        Profile.objects.filter(pk=instance.pk).update(title=instance.title)
        delattr(instance, '_updating_title')  # Clean up

def create_default_level_titles():
    """Create default level titles if they don't exist"""
    default_titles = [
        (0, 'None'),
        (1, 'Beginner'),
        (5, 'Player'),
        (10, 'Bounty 1Thousand'),
        (20, 'Bounty 100Thousand'),
        (30, 'Champion'),
        (40, 'Master'),
        (50, 'Grand Master'),
        (60, 'Elite'),
        (70, 'Legend'),
        (80, 'Mythical'),
        (90, 'Godlike'),
        (100, 'Immortal'),
    ]
    
    for level, title in default_titles:
        LevelTitle.objects.get_or_create(level=level, defaults={'title': title})
