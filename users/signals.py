from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Title


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Get the default "None" title
        none_title, created = Title.objects.get_or_create(
            name="None", 
            required_level=0,
            defaults={'description': 'No title yet'}
        )
        
        Profile.objects.create(
            user=instance, 
            title=none_title
        )
        
        # If user is a superuser, set special attributes
        if instance.is_superuser:
            profile = Profile.objects.get(user=instance)
            profile.level = 100  # High level for superuser
            monarch_title, created = Title.objects.get_or_create(
                name="Monarch", 
                required_level=100,
                defaults={'description': 'The ruler of all'}
            )
            profile.title = monarch_title
            profile.save()


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
