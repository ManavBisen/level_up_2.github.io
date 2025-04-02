from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Title, Notification

class ProfileModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create some titles
        Title.objects.create(name='None', required_level=0, description='No title')
        Title.objects.create(name='Beginner', required_level=1, description='Just started')
        Title.objects.create(name='Player', required_level=5, description='Regular player')
        
    def test_profile_creation(self):
        """Test that a profile is automatically created when a user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.level, 0)
        self.assertEqual(self.user.profile.total_xp, 0)
        
    def test_add_xp(self):
        """Test adding XP and leveling up"""
        profile = self.user.profile
        
        # Add 5 XP (not enough to level up)
        profile.add_xp(5)
        self.assertEqual(profile.level, 0)
        self.assertEqual(profile.current_xp, 5)
        self.assertEqual(profile.total_xp, 5)
        
        # Add 5 more XP (should level up to level 1)
        profile.add_xp(5)
        self.assertEqual(profile.level, 1)
        self.assertEqual(profile.current_xp, 0)
        self.assertEqual(profile.total_xp, 10)
        self.assertEqual(profile.title.name, 'Beginner')
        
    def test_subtract_xp(self):
        """Test subtracting XP and handling level down"""
        profile = self.user.profile
        
        # Add 20 XP to reach level 1
        profile.add_xp(20)
        self.assertEqual(profile.level, 1)
        self.assertEqual(profile.current_xp, 10)  # 20 - 10 (required for level 1)
        
        # Subtract 15 XP (should go back to level 0)
        profile.subtract_xp(15)
        self.assertEqual(profile.level, 0)
        self.assertEqual(profile.current_xp, 5)
        self.assertEqual(profile.total_xp, 5)
        self.assertEqual(profile.title.name, 'None')
