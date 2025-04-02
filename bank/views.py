from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Transaction


@login_required
def bank(request):
    """Show bank page with user's XP balance"""
    # Get recent transactions (last 5)
    recent_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')[:5]
    
    context = {
        'recent_transactions': recent_transactions,
        'has_password': bool(request.user.profile.password)
    }
    
    return render(request, 'bank/bank.html', context)


@login_required
def make_transaction(request):
    """Send XP to another user"""
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        password = request.POST.get('password', '')
        
        try:
            # Validate input
            if not recipient_username or not amount:
                messages.error(request, "Recipient username and amount are required.")
                return redirect('make_transaction')
            
            amount = int(amount)
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
                return redirect('make_transaction')
            
            # Get recipient
            try:
                recipient = User.objects.get(username=recipient_username)
            except User.DoesNotExist:
                messages.error(request, f"User '{recipient_username}' does not exist.")
                return redirect('make_transaction')
            
            # Don't allow sending to yourself
            if recipient == request.user:
                messages.error(request, "You cannot send XP to yourself.")
                return redirect('make_transaction')
            
            # Process the transaction
            success, message = Transaction.send_xp(
                sender=request.user,
                recipient=recipient,
                amount=amount,
                description=description,
                password=password
            )
            
            if success:
                messages.success(request, message)
                return redirect('bank')
            else:
                messages.error(request, message)
                return redirect('make_transaction')
                
        except ValueError:
            messages.error(request, "Invalid amount. Please enter a valid number.")
            return redirect('make_transaction')
    
    return render(request, 'bank/transaction.html')


@login_required
def transaction_history(request):
    """Show user's transaction history"""
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')
    
    context = {
        'transactions': transactions
    }
    
    return render(request, 'bank/transaction_history.html', context)


@login_required
def set_bank_password(request):
    """Set or change bank password for transactions"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Check current password if one exists
        if request.user.profile.password and current_password != request.user.profile.password:
            messages.error(request, "Current password is incorrect.")
            return redirect('set_bank_password')
        
        # Validate new password
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('set_bank_password')
        
        # Update password
        request.user.profile.password = new_password
        request.user.profile.save()
        
        messages.success(request, "Bank password updated successfully.")
        return redirect('bank')
    
    context = {
        'has_password': bool(request.user.profile.password)
    }
    
    return render(request, 'bank/set_password.html', context)
