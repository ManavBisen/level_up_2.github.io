from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TransactionForm, UserSearchForm
from .models import Profile, Notification, Transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return render(request, 'home.html')
    return render(request, 'home.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    user = request.user
    profile = user.profile
    
    # Calculate XP progress for progress bar
    xp_for_next_level = profile.get_xp_for_next_level()
    xp_progress = (profile.xp / xp_for_next_level) * 100 if xp_for_next_level > 0 else 0
    
    context = {
        'user': user,
        'profile': profile,
        'xp_progress': xp_progress,
        'xp_for_next_level': xp_for_next_level,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_update(request):
    """Update user profile view"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile_update.html', context)

@login_required
def bank(request):
    """Bank/Transaction view"""
    user = request.user
    profile = user.profile
    
    # Handle new transaction
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            # Verify user password
            if not user.check_password(form.cleaned_data['password']):
                messages.error(request, 'Incorrect password. Transaction failed.')
                return redirect('bank')
            
            receiver_username = form.cleaned_data['receiver_username']
            amount = form.cleaned_data['amount']
            
            # Check if user has enough XP
            if profile.total_xp < amount:
                messages.error(request, 'You do not have enough XP for this transaction.')
                return redirect('bank')
            
            try:
                receiver = User.objects.get(username=receiver_username)
                
                # Create transaction
                transaction = Transaction(
                    sender=user,
                    receiver=receiver,
                    amount=amount
                )
                transaction.save()
                
                # Update XP for both users
                profile.remove_xp(amount)
                receiver.profile.add_xp(amount)
                
                # Create notification for receiver
                Notification.objects.create(
                    user=receiver,
                    message=f"You received {amount} XP from {user.username}!"
                )
                
                messages.success(request, f'Successfully sent {amount} XP to {receiver.username}!')
                return redirect('bank')
                
            except User.DoesNotExist:
                messages.error(request, 'User not found. Transaction failed.')
                return redirect('bank')
    else:
        form = TransactionForm()
    
    # Get transaction history
    sent_transactions = Transaction.objects.filter(sender=user).order_by('-timestamp')[:10]
    received_transactions = Transaction.objects.filter(receiver=user).order_by('-timestamp')[:10]
    
    context = {
        'profile': profile,
        'form': form,
        'sent_transactions': sent_transactions,
        'received_transactions': received_transactions,
    }
    return render(request, 'users/bank.html', context)

@login_required
def notifications(request):
    """User notifications view"""
    notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark all as read
    if request.method == 'POST' and 'mark_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    # Delete all notifications
    if request.method == 'POST' and 'delete_all' in request.POST:
        notifications.delete()
        messages.success(request, 'All notifications deleted.')
        return redirect('notifications')
    
    paginator = Paginator(notifications, 10)  # 10 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/notifications.html', {'page_obj': page_obj})

@login_required
def read_notification(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications')

@login_required
def leaderboard(request):
    """Leaderboard view showing top users by XP"""
    top_profiles = Profile.objects.all().order_by('-total_xp')[:10]
    
    # Get current user's rank if not in top 10
    user_profile = request.user.profile
    user_rank = user_profile.get_rank()
    user_in_top = any(profile.user.id == request.user.id for profile in top_profiles)
    
    context = {
        'top_profiles': top_profiles,
        'user_profile': user_profile,
        'user_rank': user_rank,
        'user_in_top': user_in_top,
    }
    return render(request, 'users/leaderboard.html', context)

@staff_member_required
def user_management(request):
    """Admin view for managing users - only for superusers"""
    search_form = UserSearchForm(request.GET)
    users = User.objects.all().order_by('username')
    
    # Filter by search term if provided
    if search_form.is_valid() and search_form.cleaned_data.get('username'):
        search_term = search_form.cleaned_data.get('username')
        users = users.filter(username__icontains=search_term)
    
    # Handle XP adjustments
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        xp_amount = request.POST.get('xp_amount')
        action = request.POST.get('action')
        
        if user_id and xp_amount and action:
            try:
                user = User.objects.get(id=user_id)
                xp_amount = int(xp_amount)
                
                if action == 'add':
                    user.profile.add_xp(xp_amount)
                    messages.success(request, f'Added {xp_amount} XP to {user.username}')
                    
                    # Create notification
                    Notification.objects.create(
                        user=user,
                        message=f"Admin {request.user.username} added {xp_amount} XP to your account."
                    )
                elif action == 'remove':
                    user.profile.remove_xp(xp_amount)
                    messages.success(request, f'Removed {xp_amount} XP from {user.username}')
                    
                    # Create notification
                    Notification.objects.create(
                        user=user,
                        message=f"Admin {request.user.username} removed {xp_amount} XP from your account."
                    )
                
                # Special title assignment
                special_title = request.POST.get('special_title')
                if special_title:
                    if special_title in ['cheater', 'good guy']:
                        user.profile.title = special_title
                        user.profile.save()
                        messages.success(request, f'Set special title "{special_title}" for {user.username}')
                        
                        # Create notification
                        Notification.objects.create(
                            user=user,
                            message=f"Admin {request.user.username} gave you the special title: {special_title}"
                        )
                
            except User.DoesNotExist:
                messages.error(request, 'User not found')
            except ValueError:
                messages.error(request, 'Invalid XP amount')
    
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'admin/user_management.html', context)

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        request.user.notifications.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
