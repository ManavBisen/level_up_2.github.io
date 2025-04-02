from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import slugify

from .models import ShopItem, Purchase
import os


@login_required
def shop(request):
    """View the shop with available items"""
    items = ShopItem.objects.filter(quantity__gt=0)
    
    context = {
        'items': items
    }
    
    return render(request, 'shop/shop.html', context)


@login_required
def purchase_item(request, item_id):
    """Purchase an item from the shop"""
    item = get_object_or_404(ShopItem, id=item_id)
    
    if request.method == 'POST':
        success, message = Purchase.purchase_item(request.user, item)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('shop')
    
    context = {
        'item': item
    }
    
    return render(request, 'shop/purchase_confirm.html', context)


@login_required
def my_purchases(request):
    """View user's purchases"""
    purchases = Purchase.objects.filter(user=request.user)
    
    context = {
        'purchases': purchases
    }
    
    return render(request, 'shop/my_purchases.html', context)


@login_required
def download_purchased_item(request, purchase_id):
    """Download a purchased item"""
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    
    if not purchase.item.file:
        messages.error(request, "This item does not have a downloadable file.")
        return redirect('my_purchases')
    
    try:
        file_path = purchase.item.file.path
        response = FileResponse(open(file_path, 'rb'))
        
        # Use the saved file name if available, otherwise use the item name
        filename = purchase.item.file_name
        if not filename:
            filename = f"{slugify(purchase.item.name)}{os.path.splitext(file_path)[1]}"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        messages.error(request, "File not found. Please contact support.")
        return redirect('my_purchases')


@login_required
def manage_shop(request):
    """Manage shop items (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to manage the shop.")
        return redirect('shop')
    
    items = ShopItem.objects.all()
    
    context = {
        'items': items
    }
    
    return render(request, 'shop/manage_shop.html', context)


@login_required
def add_shop_item(request):
    """Add a new shop item (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to add shop items.")
        return redirect('shop')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = int(request.POST.get('price', 0))
        quantity = int(request.POST.get('quantity', 1))
        file = request.FILES.get('file', None)
        
        item = ShopItem(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            created_by=request.user
        )
        
        if file:
            item.file = file
            item.file_name = file.name
        
        item.save()
        messages.success(request, f"Shop item '{name}' added successfully.")
        return redirect('manage_shop')
    
    return render(request, 'shop/add_shop_item.html')


@login_required
def edit_shop_item(request, item_id):
    """Edit a shop item (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit shop items.")
        return redirect('shop')
    
    item = get_object_or_404(ShopItem, id=item_id)
    
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = int(request.POST.get('price', 0))
        item.quantity = int(request.POST.get('quantity', 1))
        
        file = request.FILES.get('file', None)
        if file:
            # Delete old file if exists
            if item.file:
                default_storage.delete(item.file.path)
            
            item.file = file
            item.file_name = file.name
        
        item.save()
        messages.success(request, f"Shop item '{item.name}' updated successfully.")
        return redirect('manage_shop')
    
    context = {
        'item': item
    }
    
    return render(request, 'shop/edit_shop_item.html', context)


@login_required
def delete_shop_item(request, item_id):
    """Delete a shop item (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete shop items.")
        return redirect('shop')
    
    item = get_object_or_404(ShopItem, id=item_id)
    
    if request.method == 'POST':
        # Delete file if exists
        if item.file:
            default_storage.delete(item.file.path)
        
        item.delete()
        messages.success(request, f"Shop item '{item.name}' deleted successfully.")
        return redirect('manage_shop')
    
    context = {
        'item': item
    }
    
    return render(request, 'shop/delete_shop_item.html', context)
