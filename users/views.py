from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Notification, Title, UserSearch
from django.db.models import Q
from tasks.models import DailyTask, ExtraTask


def home(request):
    """Home page view showing user profile info or welcome message"""
    if request.user.is_authenticated:
        context = {
            'user': request.user,
            'profile': request.user.profile,
            'title': request.user.profile.title,
            'level': request.user.profile.level,
            'current_xp': request.user.profile.current_xp,
            'total_xp': request.user.profile.total_xp,
        }
        
        # Get XP required for next level
        next_level_xp = 10
        if request.user.profile.level < 50:
            next_level_xp = 10 + request.user.profile.level
        else:
            next_level_xp = 60
            
        context['next_level_xp'] = next_level_xp
        context['xp_progress'] = (request.user.profile.current_xp / next_level_xp) * 100
        
        # Get incomplete tasks for today
        if not request.user.is_superuser:
            context['daily_tasks'] = DailyTask.get_user_tasks(request.user)
            context['extra_tasks'] = ExtraTask.objects.filter(
                assigned_to=request.user,
                completed=False
            )
        
        return render(request, 'home.html', context)
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Check if username already exists
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username {username} already exists.')
                return render(request, 'users/register.html', {'form': form})
                
            user = form.save()
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Calculate progress to next level
    next_level_xp = 10
    if request.user.profile.level < 50:
        next_level_xp = 10 + request.user.profile.level
    else:
        next_level_xp = 60
        
    progress = (request.user.profile.current_xp / next_level_xp) * 100
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'progress': progress,
        'next_level_xp': next_level_xp
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'users/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')


@login_required
def leaderboard(request):
    # Get top 10 users by level and total XP
    top_users = User.objects.filter(is_active=True).order_by('-profile__level', '-profile__total_xp')[:10]
    
    # Get current user's rank if not in top 10
    current_user_rank = None
    if request.user.is_authenticated and request.user not in top_users:
        higher_users = User.objects.filter(
            Q(profile__level__gt=request.user.profile.level) | 
            Q(profile__level=request.user.profile.level, profile__total_xp__gt=request.user.profile.total_xp)
        ).count()
        current_user_rank = higher_users + 1
    
    context = {
        'top_users': top_users,
        'current_user_rank': current_user_rank
    }
    
    return render(request, 'users/leaderboard.html', context)


@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        # Record the search
        UserSearch.objects.create(user=request.user, query=query)
        
        # Search for users
        users = User.objects.filter(username__icontains=query)
        
    return render(request, 'users/user_search.html', {'users': users, 'query': query})


@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Calculate progress to next level
    next_level_xp = 10
    if user.profile.level < 50:
        next_level_xp = 10 + user.profile.level
    else:
        next_level_xp = 60
        
    progress = (user.profile.current_xp / next_level_xp) * 100
    
    context = {
        'profile_user': user,
        'progress': progress,
        'next_level_xp': next_level_xp
    }
    
    return render(request, 'users/user_profile.html', context)


@login_required
def add_extra_title(request, user_id, title):
    """Add extra title like 'cheater' or 'good guy' to a user (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to add titles.")
        return redirect('home')
    
    target_user = get_object_or_404(User, id=user_id)
    
    if title == 'cheater':
        title_obj, created = Title.objects.get_or_create(
            name="Cheater", 
            required_level=0,
            defaults={'description': 'Caught cheating'}
        )
    elif title == 'good_guy':
        title_obj, created = Title.objects.get_or_create(
            name="Good Guy", 
            required_level=0,
            defaults={'description': 'Exemplary user'}
        )
    else:
        messages.error(request, f"Unknown title: {title}")
        return redirect('user_profile', username=target_user.username)
    
    # Update user's title and save
    target_user.profile.title = title_obj
    target_user.profile.save()
    
    # Create notification for the user
    Notification.objects.create(
        recipient=target_user,
        sender=request.user,
        message=f"You have been given the title '{title_obj.name}' by {request.user.username}."
    )
    
    messages.success(request, f"Title '{title_obj.name}' added to {target_user.username}")
    return redirect('user_profile', username=target_user.username)
