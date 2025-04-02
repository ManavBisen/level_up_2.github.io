from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from users.models import Notification


class DailyTask(models.Model):
    TASK_CHOICES = [
        ('good_work', 'Do 40 minutes of Good Work'),
        ('read_book', 'Read 2 pages of a good book'),
        ('exercise', 'Do 50 push-ups and 50 squats')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_tasks')
    title = models.CharField(max_length=200, choices=TASK_CHOICES)
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'title', 'date']
        ordering = ['-date', 'title']
    
    def __str__(self):
        return f"{self.get_title_display()} - {self.user.username} - {self.date}"
    
    @classmethod
    def get_user_tasks(cls, user):
        """Get or create daily tasks for the user for today"""
        today = timezone.now().date()
        
        # Try to get today's tasks
        tasks = cls.objects.filter(user=user, date=today)
        
        # If no tasks exist for today, create them
        if not tasks.exists():
            # Create the three default daily tasks
            for task_code, task_title in cls.TASK_CHOICES:
                cls.objects.create(
                    user=user,
                    title=task_code,
                    date=today
                )
            
            # Fetch the newly created tasks
            tasks = cls.objects.filter(user=user, date=today)
        
        return tasks
    
    @classmethod
    def process_daily_tasks(cls, user):
        """
        Process daily tasks completion and apply rewards/penalties
        Returns: (completed_count, reward_xp or penalty_xp)
        """
        today = timezone.now().date()
        tasks = cls.objects.filter(user=user, date=today)
        completed_count = tasks.filter(completed=True).count()
        total_tasks = tasks.count()
        
        # Calculate reward or penalty
        if completed_count == 0:
            # Subtract (10 + level) XP if no tasks completed, but only if level > 0
            if user.profile.level > 0:
                penalty_xp = 10 + user.profile.level
                user.profile.subtract_xp(penalty_xp)
                
                # Create notification
                Notification.objects.create(
                    recipient=user,
                    message=f"You didn't complete any daily tasks and lost {penalty_xp} XP."
                )
                
                return 0, -penalty_xp
            return 0, 0
            
        elif completed_count == 1:
            # No reward or penalty for completing 1 task
            return 1, 0
            
        elif completed_count == 2:
            # 80 XP for completing 2 tasks
            reward_xp = 80
            user.profile.add_xp(reward_xp)
            
            # Create notification
            Notification.objects.create(
                recipient=user,
                message=f"You completed 2 daily tasks and earned {reward_xp} XP!"
            )
            
            return 2, reward_xp
            
        elif completed_count == 3:
            # 200 XP for completing all 3 tasks
            reward_xp = 200
            user.profile.add_xp(reward_xp)
            
            # Create notification
            Notification.objects.create(
                recipient=user,
                message=f"You completed all daily tasks and earned {reward_xp} XP! Great job!"
            )
            
            return 3, reward_xp
        
        return completed_count, 0


class ExtraTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    xp_reward = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', 
                                   null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.assigned_to:
            return f"{self.title} - Assigned to {self.assigned_to.username}"
        return f"{self.title} - Assigned to all users"
    
    def complete_task(self, user):
        """Mark task as completed and award XP to user"""
        if self.completed:
            return False
            
        self.completed = True
        self.save()
        
        # Award XP to user
        user.profile.add_xp(self.xp_reward)
        
        # Create notification
        Notification.objects.create(
            recipient=user,
            sender=self.created_by,
            message=f"You completed the extra task '{self.title}' and earned {self.xp_reward} XP!"
        )
        
        # Notify the creator if it's not the same user
        if self.created_by != user:
            Notification.objects.create(
                recipient=self.created_by,
                sender=user,
                message=f"{user.username} completed the extra task '{self.title}'."
            )
        
        return True


class GoodWorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_work_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Good Work Session: {self.user.username} - {self.start_time}"
    
    def end_session(self):
        """End the session and calculate XP earned"""
        if not self.end_time:
            self.end_time = timezone.now()
            # Calculate duration in minutes
            duration = (self.end_time - self.start_time).total_seconds() / 60
            self.duration_minutes = int(duration)
            
            # 1 XP per minute of Good Work
            self.xp_earned = self.duration_minutes
            self.save()
            
            # Add XP to user
            self.user.profile.add_xp(self.xp_earned)
            
            # Check for daily task completion
            today = timezone.now().date()
            good_work_task = DailyTask.objects.filter(
                user=self.user,
                date=today,
                title='good_work'
            ).first()
            
            if good_work_task and not good_work_task.completed and self.duration_minutes >= 40:
                good_work_task.completed = True
                good_work_task.save()
                
                # Notify user
                Notification.objects.create(
                    recipient=self.user,
                    message=f"You've completed the daily task: 40 minutes of Good Work!"
                )
            
            return self.xp_earned
        
        return 0
