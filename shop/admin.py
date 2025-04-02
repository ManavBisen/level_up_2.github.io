from django.contrib import admin
from .models import ShopItem, Purchase

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'stock', 'file_type', 'created_by')
    list_filter = ('file_type', 'created_by')
    search_fields = ('name', 'description')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'purchased_at', 'price_paid')
    list_filter = ('purchased_at',)
    search_fields = ('user__username', 'item__name')
