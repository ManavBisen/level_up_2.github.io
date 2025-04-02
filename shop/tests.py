from django.test import TestCase
from django.contrib.auth.models import User
from .models import ShopItem, Purchase


class ShopTests(TestCase):
    def setUp(self):
        # Create a superuser (shop owner)
        self.admin = User.objects.create_superuser(
            username='shopadmin',
            email='admin@shop.com',
            password='adminpass'
        )
        
        # Create a regular user (customer)
        self.user = User.objects.create_user(
            username='shopcustomer',
            email='customer@shop.com',
            password='customerpass'
        )
        
        # Give the user some XP
        self.user.profile.add_xp(500)
        
        # Create a shop item
        self.item = ShopItem.objects.create(
            name='Test Item',
            description='A test item for the shop',
            price=100,
            quantity=2,
            created_by=self.admin
        )
    
    def test_purchase_item(self):
        """Test purchasing an item from the shop"""
        # Initial state
        self.assertEqual(self.user.profile.total_xp, 500)
        self.assertEqual(self.item.quantity, 2)
        
        # Purchase the item
        success, message = Purchase.purchase_item(self.user, self.item)
        
        # Check purchase was successful
        self.assertTrue(success)
        self.assertIn("Successfully purchased", message)
        
        # Check user's XP was deducted
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, 400)
        
        # Check item quantity was reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 1)
        
        # Check purchase record exists
        purchase = Purchase.objects.filter(user=self.user, item=self.item).first()
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.price_paid, 100)
    
    def test_purchase_out_of_stock(self):
        """Test attempting to purchase an out-of-stock item"""
        # Set quantity to 0
        self.item.quantity = 0
        self.item.save()
        
        # Try to purchase
        success, message = Purchase.purchase_item(self.user, self.item)
        
        # Check purchase failed
        self.assertFalse(success)
        self.assertIn("out of stock", message)
        
        # Check no XP was deducted
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.total_xp, 500)
    
    def test_purchase_insufficient_xp(self):
        """Test attempting to purchase with insufficient XP"""
        # Set user's XP to less than item price
        self.user.profile.total_xp = 50
        self.user.profile.save()
        
        # Try to purchase
        success, message = Purchase.purchase_item(self.user, self.item)
        
        # Check purchase failed
        self.assertFalse(success)
        self.assertIn("don't have enough XP", message)
        
        # Check item quantity wasn't reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 2)
