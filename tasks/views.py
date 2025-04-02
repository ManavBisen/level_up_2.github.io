from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User

from .models import DailyTask, ExtraTask, GoodWorkSession
from .forms import ExtraTaskForm
from users.models import Notification


@login_required
def daily_tasks(request):
    tasks = DailyTask.get_user_tasks(request.user)
    
    context = {
        'tasks': tasks
    }
    
    return render(request, 'tasks/daily_tasks.html', context)


@login_required
def submit_daily_tasks(request):
    """Submit daily tasks for processing"""
    if request.method == 'POST':
        completed_count, xp_change = DailyTask.process_daily_tasks(request.user)
        
        if xp_change > 0:
            messages.success(request, f"You completed {completed_count} tasks and earned {xp_change} XP!")
        elif xp_change < 0:
            messages.warning(request, f"You didn't complete any tasks and lost {-xp_change} XP.")
        else:
            messages.info(request, f"You completed {completed_count} tasks. No XP change.")
        
        return redirect('daily_tasks')
    
    return redirect('daily_tasks')


@login_required
def update_daily_task(request):
    """AJAX endpoint to update a daily task's completion status"""
    if request.method == 'POST' and request.is_ajax():
        task_id = request.POST.get('task_id')
        completed = request.POST.get('completed') == 'true'
        
        task = get_object_or_404(DailyTask, id=task_id, user=request.user)
        task.completed = completed
        task.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def extra_tasks(request):
    # For regular users, show tasks assigned to them or all users
    if not request.user.is_superuser:
        tasks = ExtraTask.objects.filter(
            completed=False
        ).filter(
            assigned_to=request.user
        )
    else:
        # For superusers, show all tasks
        tasks = ExtraTask.objects.all().order_by('-created_at')
    
    context = {
        'tasks': tasks
    }
    
    return render(request, 'tasks/extra_tasks.html', context)


@login_required
def add_extra_task(request):
    """Add extra task (superuser only)"""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to add extra tasks.")
        return redirect('extra_tasks')
    
    if request.method == 'POST':
        form = ExtraTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            # If task is assigned to a specific user, notify them
            if task.assigned_to:
                Notification.objects.create(
                    recipient=task.assigned_to,
                    sender=request.user,
                    message=f"You have been assigned a new extra task: {task.title}"
                )
                messages.success(request, f"Task assigned to {task.assigned_to.username}")
            else:
                # Notify all active users
                for user in User.objects.filter(is_active=True).exclude(id=request.user.id):
                    Notification.objects.create(
                        recipient=user,
                        sender=request.user,
                        message=f"A new extra task is available: {task.title}"
                    )
                messages.success(request, "Task added and all users notified")
            
            return redirect('extra_tasks')
    else:
        form = ExtraTaskForm()
    
    return render(request, 'tasks/add_extra_task.html', {'form': form})


@login_required
def complete_extra_task(request, task_id):
    """Mark an extra task as completed"""
    task = get_object_or_404(ExtraTask, id=task_id)
    
    # Check if user is assigned to this task or if it's assigned to all users
    if task.assigned_to and task.assigned_to != request.user:
        messages.error(request, "You are not assigned to this task.")
        return redirect('extra_tasks')
    
    # Complete the task and award XP
    if task.complete_task(request.user):
        messages.success(request, f"Task completed! You earned {task.xp_reward} XP.")
    else:
        messages.error(request, "This task has already been completed.")
    
    return redirect('extra_tasks')


@login_required
def good_work(request):
    """Good Work timer page"""
    # Get the most recent active session, if any
    active_session = GoodWorkSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()
    
    # Get recent completed sessions (last 7 days)
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    recent_sessions = GoodWorkSession.objects.filter(
        user=request.user,
        end_time__isnull=False,
        end_time__gt=one_week_ago
    ).order_by('-end_time')
    
    context = {
        'active_session': active_session,
        'recent_sessions': recent_sessions
    }
    
    return render(request, 'tasks/good_work.html', context)


@login_required
def start_good_work(request):
    """Start a Good Work session"""
    # Check if user already has an active session
    active_session = GoodWorkSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()
    
    if active_session:
        messages.warning(request, "You already have an active Good Work session.")
    else:
        # Create new session
        GoodWorkSession.objects.create(user=request.user)
        messages.success(request, "Good Work session started! Timer is now running.")
    
    return redirect('good_work')


@login_required
def end_good_work(request):
    """End the current Good Work session"""
    active_session = GoodWorkSession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).first()
    
    if not active_session:
        messages.error(request, "You don't have an active Good Work session.")
    else:
        xp_earned = active_session.end_session()
        messages.success(request, f"Good Work session ended! You earned {xp_earned} XP.")
    
    return redirect('good_work')
