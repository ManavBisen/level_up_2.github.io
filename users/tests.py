from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Notification, Transaction, LevelTitle

class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = self.user.profile
    
    def test_profile_creation(self):
        self.assertEqual(self.profile.level, 0)
        self.assertEqual(self.profile.xp, 0)
        self.assertEqual(self.profile.total_xp, 0)
        self.assertEqual(self.profile.title, 'None')
    
    def test_xp_addition_and_level_up(self):
        # Add 15 XP (should level up to level 1)
        self.profile.add_xp(15)
        self.assertEqual(self.profile.level, 1)
        self.assertEqual(self.profile.xp, 5)  # 15 - 10 = 5
        self.assertEqual(self.profile.total_xp, 15)
        self.assertEqual(self.profile.title, 'Beginner')
        
        # Check notifications
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)
    
    def test_xp_removal(self):
        # First add XP and level up
        self.profile.add_xp(15)
        # Now remove 10 XP
        self.profile.remove_xp(10)
        self.assertEqual(self.profile.total_xp, 5)

class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            message='Test notification'
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, 'Test notification')
        self.assertFalse(notification.is_read)
    
    def test_cleanup_old_notifications(self):
        # This would require mocking time to properly test
        pass

class TransactionModelTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='12345')
        self.receiver = User.objects.create_user(username='receiver', password='12345')
        
    def test_transaction_creation(self):
        # Give sender some XP first
        self.sender.profile.add_xp(100)
        
        # Create transaction
        transaction = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=50
        )
        
        self.assertEqual(transaction.sender, self.sender)
        self.assertEqual(transaction.receiver, self.receiver)
        self.assertEqual(transaction.amount, 50)
