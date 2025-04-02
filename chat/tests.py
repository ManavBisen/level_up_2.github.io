from django.test import TestCase
from django.contrib.auth.models import User
from .models import DirectMessage, CommunityMessage
from users.models import Notification


class ChatTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='chatuser1',
            email='user1@chat.com',
            password='chatpass1'
        )
        
        self.user2 = User.objects.create_user(
            username='chatuser2',
            email='user2@chat.com',
            password='chatpass2'
        )
    
    def test_direct_message(self):
        """Test sending a direct message creates notification"""
        # Check initial state
        self.assertEqual(Notification.objects.count(), 0)
        
        # Send a direct message
        message = DirectMessage.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="Hello, this is a test message"
        )
        
        # Check a notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.recipient, self.user2)
        self.assertEqual(notification.sender, self.user1)
        self.assertIn("New message", notification.message)
    
    def test_community_message(self):
        """Test community messages"""
        # Send a community message
        message = CommunityMessage.objects.create(
            sender=self.user1,
            content="Hello community!"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, "Hello community!")
