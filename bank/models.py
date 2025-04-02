from django.db import models
from django.contrib.auth.models import User
from users.models import Notification


class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.sender.username} sent {self.amount} XP to {self.recipient.username}"
    
    @classmethod
    def send_xp(cls, sender, recipient, amount, description="", password=None):
        """
        Send XP from one user to another
        Returns: (success, message)
        """
        # Check if sender has a bank password set and it matches
        if sender.profile.password and (not password or password != sender.profile.password):
            return False, "Incorrect bank password"
        
        # Check if sender has enough XP
        if sender.profile.total_xp < amount:
            return False, f"Insufficient XP balance. You have {sender.profile.total_xp} XP."
        
        # Check if amount is positive
        if amount <= 0:
            return False, "Amount must be positive"
        
        # Create transaction
        transaction = cls.objects.create(
            sender=sender,
            recipient=recipient,
            amount=amount,
            description=description
        )
        
        # Deduct XP from sender
        sender.profile.subtract_xp(amount)
        
        # Add XP to recipient
        recipient.profile.add_xp(amount)
        
        # Create notification for recipient
        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            message=f"{sender.username} sent you {amount} XP. " + 
                    (f"Message: {description}" if description else "")
        )
        
        return True, f"Successfully sent {amount} XP to {recipient.username}"
