from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import os

def shop_file_path(instance, filename):
    """Generate file path for shop item files"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Set new filename with id
    filename = f'shop_item_{instance.id}.{ext}'
    # Return full path
    return os.path.join('shop_items', filename)

class ShopItem(models.Model):
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('other', 'Other')
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to=shop_file_path, null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default='other')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def is_available(self):
        """Check if the item is available for purchase"""
        return self.stock > 0
    
    def purchase(self, user):
        """Process a purchase for this item"""
        from users.models import Notification
        
        if not self.is_available():
            return False
            
        if user.profile.total_xp < self.price:
            return False
            
        # Create purchase
        purchase = Purchase.objects.create(
            user=user,
            item=self,
            price_paid=self.price
        )
        
        # Deduct XP from user
        user.profile.remove_xp(self.price)
        
        # Decrease stock
        self.stock -= 1
        self.save()
        
        # Create notification
        Notification.objects.create(
            user=user,
            message=f"You purchased '{self.name}' for {self.price} XP."
        )
        
        # Notify the creator
        if self.created_by != user:
            Notification.objects.create(
                user=self.created_by,
                message=f"{user.username} purchased your item '{self.name}'."
            )
        
        return purchase

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} purchased {self.item.name}"
