from django.db import models
from django.contrib.auth.models import User
from users.models import Notification


class ShopItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()  # Price in XP
    file = models.FileField(upload_to='shop_items/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def is_available(self):
        """Check if item is still available for purchase"""
        return self.quantity > 0


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.PositiveIntegerField()  # Store price paid in case item price changes later
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.item.name}"
    
    @classmethod
    def purchase_item(cls, user, item):
        """
        Process purchase of an item by a user
        Returns: (success, message)
        """
        # Check if item is available
        if not item.is_available():
            return False, "This item is out of stock"
        
        # Check if user has enough XP
        if user.profile.total_xp < item.price:
            return False, f"You don't have enough XP. Need {item.price} XP."
        
        # Process the purchase
        purchase = cls.objects.create(
            user=user,
            item=item,
            price_paid=item.price
        )
        
        # Deduct XP from user
        user.profile.subtract_xp(item.price)
        
        # Reduce item quantity
        item.quantity -= 1
        item.save()
        
        # Create notification
        Notification.objects.create(
            recipient=user,
            message=f"You purchased {item.name} for {item.price} XP."
        )
        
        # Notify item creator
        if item.created_by != user:
            Notification.objects.create(
                recipient=item.created_by,
                sender=user,
                message=f"{user.username} purchased your item: {item.name}"
            )
        
        return True, f"Successfully purchased {item.name} for {item.price} XP"
