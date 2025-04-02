from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .models import DailyTask, TaskCompletion, TimerSession, ExtraTask
from .forms import ExtraTaskForm
from users.models import Notification

@login_required
def daily_tasks(request):
    """View for daily tasks"""
    user = request.user
    
    # Ensure default tasks exist
    default_tasks = DailyTask.get_default_tasks()
    
    # Get today's completions
    today_completions = TaskCompletion.get_today_completed(user)
    completed_task_ids = [completion.task.id for completion in today_completions]
    
    # Get extra tasks available for this user
    extra_tasks = ExtraTask.objects.filter(
        target_user=user,
        stock__gt=0
    ) | ExtraTask.objects.filter(
        is_global=True,
        stock__gt=0
    )
    
    # If tasks are being submitted
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        action = request.POST.get('action', 'complete')
        
        if task_id and action == 'complete':
            try:
                task = DailyTask.objects.get(id=task_id)
                
                # Check if already completed today
                if task.id not in completed_task_ids:
                    # Create completion record
                    TaskCompletion.objects.create(
                        user=user,
                        task=task
                    )
                    
                    messages.success(request, f'Task "{task.name}" marked as completed!')
                    
                    # Calculate reward
                    reward = TaskCompletion.calculate_daily_reward_or_punishment(user)
                    if reward > 0:
                        messages.success(request, f'You earned {reward} XP for completing tasks!')
                    
                    return redirect('daily_tasks')
                else:
                    messages.info(request, 'This task has already been completed today.')
            except DailyTask.DoesNotExist:
                messages.error(request, 'Task not found.')
        
        # Handle extra task completion
        if task_id and action == 'complete_extra':
            try:
                extra_task = ExtraTask.objects.get(id=task_id)
                if extra_task.complete_for_user(user):
                    messages.success(request, f'Extra task "{extra_task.name}" completed! You earned {extra_task.xp_reward} XP.')
                else:
                    messages.error(request, 'This task is no longer available.')
                return redirect('daily_tasks')
            except ExtraTask.DoesNotExist:
                messages.error(request, 'Task not found.')
    
    # Calculate progress
    total_default_tasks = len(default_tasks)
    completed_default_tasks = sum(1 for task in default_tasks if task.id in completed_task_ids)
    completion_percentage = (completed_default_tasks / total_default_tasks) * 100 if total_default_tasks > 0 else 0
    
    # Get good work timer info
    today_good_work_minutes = TimerSession.get_total_today_duration(user)
    good_work_task = next((task for task in default_tasks if task.name == 'Do 40 minutes Good Work'), None)
    good_work_completed = good_work_task and good_work_task.id in completed_task_ids
    
    context = {
        'default_tasks': default_tasks,
        'extra_tasks': extra_tasks,
        'completed_task_ids': completed_task_ids,
        'completion_percentage': completion_percentage,
        'today_good_work_minutes': today_good_work_minutes,
        'good_work_completed': good_work_completed,
    }
    return render(request, 'tasks/daily_tasks.html', context)

@login_required
def good_work_timer(request):
    """View for Good Work timer"""
    user = request.user
    
    # Get current active session if any
    active_session = TimerSession.objects.filter(
        user=user,
        end_time__isnull=True
    ).first()
    
    # Get today's completed sessions
    today_sessions = TimerSession.get_today_sessions(user)
    total_today_minutes = TimerSession.get_total_today_duration(user)
    
    context = {
        'active_session': active_session,
        'today_sessions': today_sessions,
        'total_today_minutes': total_today_minutes,
    }
    return render(request, 'tasks/good_work_timer.html', context)

@login_required
@require_POST
def start_timer(request):
    """Start a new timer session"""
    user = request.user
    
    # Check if there's already an active session
    active_session = TimerSession.objects.filter(
        user=user,
        end_time__isnull=True
    ).first()
    
    if active_session:
        return JsonResponse({
            'status': 'error',
            'message': 'You already have an active timer session'
        })
    
    # Create new session
    session = TimerSession.objects.create(user=user)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Timer started',
        'session_id': session.id,
        'start_time': session.start_time.isoformat()
    })

@login_required
@require_POST
def stop_timer(request):
    """Stop an active timer session"""
    user = request.user
    session_id = request.POST.get('session_id')
    
    try:
        session = TimerSession.objects.get(id=session_id, user=user, end_time__isnull=True)
        session.end_session()
        
        # Create notification
        Notification.objects.create(
            user=user,
            message=f"Good work! You completed {session.duration_minutes} minutes and earned {session.xp_earned} XP."
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Timer stopped',
            'duration_minutes': session.duration_minutes,
            'xp_earned': session.xp_earned
        })
    except TimerSession.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Timer session not found'
        })

@staff_member_required
def create_extra_task(request):
    """Create a new extra task (superuser only)"""
    if request.method == 'POST':
        form = ExtraTaskForm(request.POST)
        if form.is_valid():
            extra_task = form.save(commit=False)
            extra_task.assigned_by = request.user
            extra_task.save()
            
            # Create notification for target user if specified
            if extra_task.target_user:
                Notification.objects.create(
                    user=extra_task.target_user,
                    message=f"You have been assigned a new task: {extra_task.name}"
                )
            # For global tasks, notify all users
            elif extra_task.is_global:
                for user in User.objects.filter(is_staff=False):
                    Notification.objects.create(
                        user=user,
                        message=f"A new global task is available: {extra_task.name}"
                    )
            
            messages.success(request, f'Extra task "{extra_task.name}" created successfully!')
            return redirect('user-management')
    else:
        form = ExtraTaskForm()
    
    context = {'form': form}
    return render(request, 'tasks/create_extra_task.html', context)
