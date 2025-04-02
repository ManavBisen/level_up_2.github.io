from django.test import TestCase
from django.contrib.auth.models import User
from .models import Transaction


class BankTests(TestCase):
    def setUp(self):
        # Create test users
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='senderpass'
        )
        
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='recipientpass'
        )
        
        # Give sender some XP
        self.sender.profile.add_xp(500)
    
    def test_send_xp(self):
        """Test sending XP from one user to another"""
        # Initial state
        self.assertEqual(self.sender.profile.total_xp, 500)
        self.assertEqual(self.recipient.profile.total_xp, 0)
        
        # Send XP
        success, message = Transaction.send_xp(
            sender=self.sender,
            recipient=self.recipient,
            amount=100,
            description="Test transaction"
        )
        
        # Check transaction was successful
        self.assertTrue(success)
        self.assertIn("Successfully sent", message)
        
        # Check XP balances updated correctly
        self.sender.profile.refresh_from_db()
        self.recipient.profile.refresh_from_db()
        self.assertEqual(self.sender.profile.total_xp, 400)
        self.assertEqual(self.recipient.profile.total_xp, 100)
        
        # Check transaction record exists
        transaction = Transaction.objects.filter(
            sender=self.sender,
            recipient=self.recipient
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.description, "Test transaction")
    
    def test_send_xp_insufficient_balance(self):
        """Test sending more XP than available"""
        # Try to send more XP than sender has
        success, message = Transaction.send_xp(
            sender=self.sender,
            recipient=self.recipient,
            amount=600
        )
        
        # Check transaction failed
        self.assertFalse(success)
        self.assertIn("Insufficient XP balance", message)
        
        # Check balances unchanged
        self.sender.profile.refresh_from_db()
        self.recipient.profile.refresh_from_db()
        self.assertEqual(self.sender.profile.total_xp, 500)
        self.assertEqual(self.recipient.profile.total_xp, 0)
    
    def test_send_xp_with_password(self):
        """Test sending XP with bank password"""
        # Set a bank password for sender
        self.sender.profile.password = "bankpass123"
        self.sender.profile.save()
        
        # Try to send without password (should fail)
        success, message = Transaction.send_xp(
            sender=self.sender,
            recipient=self.recipient,
            amount=100
        )
        self.assertFalse(success)
        self.assertIn("Incorrect bank password", message)
        
        # Try with incorrect password (should fail)
        success, message = Transaction.send_xp(
            sender=self.sender,
            recipient=self.recipient,
            amount=100,
            password="wrongpass"
        )
        self.assertFalse(success)
        self.assertIn("Incorrect bank password", message)
        
        # Try with correct password (should succeed)
        success, message = Transaction.send_xp(
            sender=self.sender,
            recipient=self.recipient,
            amount=100,
            password="bankpass123"
        )
        self.assertTrue(success)
        self.assertIn("Successfully sent", message)
