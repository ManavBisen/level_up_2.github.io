from django.test import TestCase
from django.contrib.auth.models import User
from .models import DirectMessage, CommunityMessage

class DirectMessageModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        
        # Create some test messages
        DirectMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message 1"
        )
        DirectMessage.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Test message 2"
        )
    
    def test_get_conversation(self):
        conversation = DirectMessage.get_conversation(self.user1, self.user2)
        self.assertEqual(conversation.count(), 2)
    
    def test_get_conversations(self):
        conversations = DirectMessage.get_conversations(self.user1)
        self.assertEqual(conversations.count(), 1)
        self.assertEqual(conversations.first(), self.user2)

class CommunityMessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Create some test messages
        CommunityMessage.objects.create(
            sender=self.user,
            content="Test community message"
        )
    
    def test_community_message_creation(self):
        message = CommunityMessage.objects.first()
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.content, "Test community message")
