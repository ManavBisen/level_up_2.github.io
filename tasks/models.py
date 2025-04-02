from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time, timedelta

class DailyTask(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    xp_reward = models.IntegerField(default=80)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_default_tasks(cls):
        """Get or create the default daily tasks"""
        default_tasks = [
            {
                'name': 'Do 40 minutes Good Work',
                'description': 'Complete 40 minutes of focused work using the Good Work timer.',
                'xp_reward': 80,
                'is_default': True
            },
            {
                'name': 'Read 2 pages of a good book',
                'description': 'Read at least 2 pages from a book that helps you grow.',
                'xp_reward': 80,
                'is_default': True
            },
            {
                'name': 'Do 50 push ups and 50 squats',
                'description': 'Complete 50 push ups and 50 squats for physical fitness.',
                'xp_reward': 80,
                'is_default': True
            }
        ]
        
        created_tasks = []
        for task_data in default_tasks:
            task, created = cls.objects.get_or_create(
                name=task_data['name'],
                defaults={
                    'description': task_data['description'],
                    'xp_reward': task_data['xp_reward'],
                    'is_default': task_data['is_default']
                }
            )
            created_tasks.append(task)
        
        return created_tasks

class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_completions')
    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'task', 'completed_at')
        
    def __str__(self):
        return f"{self.user.username} completed {self.task.name} at {self.completed_at}"
    
    @classmethod
    def get_today_completed(cls, user):
        """Get tasks completed today by the user"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_start = datetime.combine(today, time.min, tzinfo=timezone.get_current_timezone())
        today_end = datetime.combine(tomorrow, time.min, tzinfo=timezone.get_current_timezone())
        
        return cls.objects.filter(
            user=user,
            completed_at__gte=today_start,
            completed_at__lt=today_end
        )
    
    @classmethod
    def calculate_daily_reward_or_punishment(cls, user):
        """Calculate XP reward or punishment based on daily task completion"""
        default_tasks = DailyTask.objects.filter(is_default=True)
        total_default_tasks = default_tasks.count()
        
        today_completed = cls.get_today_completed(user)
        completed_default_tasks = today_completed.filter(task__is_default=True).count()
        
        if completed_default_tasks == 0:
            # Punishment: subtract (10+level) XP, but only if user is level 1 or higher
            if user.profile.level >= 1:
                punishment_xp = 10 + user.profile.level
                user.profile.remove_xp(punishment_xp)
                return -punishment_xp
            return 0
            
        elif completed_default_tasks == 1:
            # No reward or punishment
            return 0
            
        elif completed_default_tasks == 2:
            # 80 XP reward
            user.profile.add_xp(80)
            return 80
            
        elif completed_default_tasks == total_default_tasks:
            # All tasks completed: 150 XP reward
            user.profile.add_xp(150)
            return 150
            
        return 0

class TimerSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timer_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    xp_earned = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s session: {self.duration_minutes} minutes"
    
    def end_session(self):
        """End the timer session and calculate XP"""
        if not self.end_time:
            self.end_time = timezone.now()
            
            # Calculate duration in minutes
            duration = (self.end_time - self.start_time).total_seconds() / 60
            self.duration_minutes = int(duration)
            
            # Calculate XP (1 XP per minute)
            self.xp_earned = self.duration_minutes
            
            # Add XP to user's profile
            self.user.profile.add_xp(self.xp_earned)
            
            self.save()
            
            # Check if the "Do 40 minutes Good Work" task is completed
            if self.duration_minutes >= 40:
                try:
                    good_work_task = DailyTask.objects.get(name='Do 40 minutes Good Work')
                    today_completions = TaskCompletion.get_today_completed(self.user)
                    
                    # Only mark as completed if not already completed today
                    if not today_completions.filter(task=good_work_task).exists():
                        TaskCompletion.objects.create(
                            user=self.user,
                            task=good_work_task
                        )
                except DailyTask.DoesNotExist:
                    pass
    
    @classmethod
    def get_today_sessions(cls, user):
        """Get timer sessions from today"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_start = datetime.combine(today, time.min, tzinfo=timezone.get_current_timezone())
        today_end = datetime.combine(tomorrow, time.min, tzinfo=timezone.get_current_timezone())
        
        return cls.objects.filter(
            user=user,
            start_time__gte=today_start,
            start_time__lt=today_end
        )
    
    @classmethod
    def get_total_today_duration(cls, user):
        """Get total duration of timer sessions from today"""
        today_sessions = cls.get_today_sessions(user)
        return sum(session.duration_minutes for session in today_sessions)

class ExtraTask(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    xp_reward = models.IntegerField(default=50)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extra_tasks', null=True, blank=True)
    is_global = models.BooleanField(default=False)  # If True, assigned to all users
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    stock = models.IntegerField(default=1)  # How many users can complete this task
    
    def __str__(self):
        if self.is_global:
            return f"Global task: {self.name}"
        elif self.target_user:
            return f"Task for {self.target_user.username}: {self.name}"
        return self.name
    
    def is_available_for(self, user):
        """Check if task is available for a specific user"""
        if self.stock <= 0:
            return False
            
        if self.expires_at and timezone.now() > self.expires_at:
            return False
            
        if self.is_global:
            return True
            
        if self.target_user and self.target_user == user:
            return True
            
        return False
    
    def complete_for_user(self, user):
        """Mark task as completed by user and grant XP reward"""
        if not self.is_available_for(user):
            return False
            
        # Create completion record
        TaskCompletion.objects.create(
            user=user,
            task=self
        )
        
        # Add XP to user
        user.profile.add_xp(self.xp_reward)
        
        # Decrease stock
        self.stock -= 1
        self.save()
        
        # Create notification
        from users.models import Notification
        Notification.objects.create(
            user=user,
            message=f"You completed the extra task '{self.name}' and earned {self.xp_reward} XP!"
        )
        
        return True
