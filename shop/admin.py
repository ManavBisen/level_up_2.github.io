from django.contrib import admin
from .models import ShopItem, Purchase

@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'purchased_at', 'price_paid')
    search_fields = ('user__username', 'item__name')
    list_filter = ('purchased_at',)
