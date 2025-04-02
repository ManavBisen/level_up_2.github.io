from django.test import TestCase
from django.contrib.auth.models import User
from .models import ShopItem, Purchase

class ShopItemModelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='12345',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        
        # Give the user some XP
        self.user.profile.add_xp(100)
        
        # Create a shop item
        self.item = ShopItem.objects.create(
            name='Test Item',
            description='Test Description',
            price=50,
            stock=2,
            created_by=self.admin
        )
    
    def test_shop_item_creation(self):
        self.assertEqual(self.item.name, 'Test Item')
        self.assertEqual(self.item.price, 50)
        self.assertEqual(self.item.stock, 2)
        self.assertTrue(self.item.is_available())
    
    def test_item_purchase(self):
        # User has 100 XP, item costs 50
        purchase = self.item.purchase(self.user)
        self.assertIsNotNone(purchase)
        
        # Check user's XP was deducted
        self.assertEqual(self.user.profile.total_xp, 50)
        
        # Check stock was reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock, 1)
        
        # Check purchase record
        self.assertEqual(purchase.user, self.user)
        self.assertEqual(purchase.item, self.item)
        self.assertEqual(purchase.price_paid, 50)
    
    def test_purchase_with_insufficient_xp(self):
        # Reduce user's XP
        self.user.profile.remove_xp(80)  # Now has 20 XP
        
        # Try to purchase 50 XP item
        purchase = self.item.purchase(self.user)
        self.assertFalse(purchase)
        
        # XP should not change
        self.assertEqual(self.user.profile.total_xp, 20)
        
        # Stock should not change
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock, 2)
    
    def test_out_of_stock_purchase(self):
        # Set stock to 0
        self.item.stock = 0
        self.item.save()
        
        # Try to purchase
        purchase = self.item.purchase(self.user)
        self.assertFalse(purchase)
        
        # XP should not change
        self.assertEqual(self.user.profile.total_xp, 100)
