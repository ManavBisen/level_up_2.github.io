from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import FileResponse
from django.urls import reverse

from .models import ShopItem, Purchase
from .forms import ShopItemForm
from users.models import Notification

@login_required
def shop(request):
    """Shop page displaying available items"""
    items = ShopItem.objects.filter(stock__gt=0).order_by('-created_at')
    
    context = {
        'items': items,
        'user_xp': request.user.profile.total_xp,
    }
    return render(request, 'shop/shop.html', context)

@login_required
def item_detail(request, item_id):
    """Detail view for a shop item"""
    item = get_object_or_404(ShopItem, id=item_id)
    
    # Handle purchase
    if request.method == 'POST' and 'purchase' in request.POST:
        if item.is_available():
            if request.user.profile.total_xp >= item.price:
                # Process purchase
                purchase = item.purchase(request.user)
                if purchase:
                    messages.success(request, f"You have purchased '{item.name}' for {item.price} XP!")
                    return redirect('item_detail', item_id=item.id)
                else:
                    messages.error(request, "Error processing purchase.")
            else:
                messages.error(request, f"You don't have enough XP to purchase this item. You need {item.price} XP.")
        else:
            messages.error(request, "This item is out of stock.")
    
    # Get user's purchases of this item
    user_purchases = Purchase.objects.filter(user=request.user, item=item)
    has_purchased = user_purchases.exists()
    
    context = {
        'item': item,
        'user_xp': request.user.profile.total_xp,
        'has_purchased': has_purchased,
    }
    return render(request, 'shop/item_detail.html', context)

@login_required
def download_item(request, purchase_id):
    """Download a purchased item"""
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    item = purchase.item
    
    if item.file:
        response = FileResponse(item.file.open('rb'))
        return response
    
    messages.error(request, "No file is available for this item.")
    return redirect('item_detail', item_id=item.id)

@login_required
def my_purchases(request):
    """View showing the user's purchases"""
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchased_at')
    
    context = {
        'purchases': purchases,
    }
    return render(request, 'shop/my_purchases.html', context)

@staff_member_required
def create_shop_item(request):
    """Create a new shop item (superuser only)"""
    if request.method == 'POST':
        form = ShopItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            
            # Notify all users about new item
            for user in User.objects.filter(is_staff=False):
                Notification.objects.create(
                    user=user,
                    message=f"New item in the shop: '{item.name}' for {item.price} XP!"
                )
            
            messages.success(request, f"Shop item '{item.name}' has been created!")
            return redirect('shop')
    else:
        form = ShopItemForm()
    
    context = {'form': form}
    return render(request, 'shop/create_shop_item.html', context)

@staff_member_required
def edit_shop_item(request, item_id):
    """Edit a shop item (superuser only)"""
    item = get_object_or_404(ShopItem, id=item_id)
    
    if request.method == 'POST':
        form = ShopItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Shop item '{item.name}' has been updated!")
            return redirect('shop')
    else:
        form = ShopItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'shop/edit_shop_item.html', context)

@staff_member_required
def delete_shop_item(request, item_id):
    """Delete a shop item (superuser only)"""
    item = get_object_or_404(ShopItem, id=item_id)
    
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f"Shop item '{item_name}' has been deleted!")
        return redirect('shop')
    
    context = {'item': item}
    return render(request, 'shop/delete_shop_item.html', context)
