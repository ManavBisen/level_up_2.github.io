from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import DailyTask, TaskCompletion, TimerSession, ExtraTask
from datetime import timedelta

class DailyTaskModelTests(TestCase):
    def test_get_default_tasks(self):
        # Test that default tasks are created
        default_tasks = DailyTask.get_default_tasks()
        self.assertEqual(len(default_tasks), 3)
        
        # Check that the "Do 40 minutes Good Work" task exists
        good_work_task = DailyTask.objects.filter(name='Do 40 minutes Good Work').first()
        self.assertIsNotNone(good_work_task)

class TaskCompletionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = DailyTask.objects.create(
            name='Test Task',
            description='Test Description',
            xp_reward=80,
            is_default=True
        )
    
    def test_task_completion(self):
        # Create a task completion
        completion = TaskCompletion.objects.create(
            user=self.user,
            task=self.task
        )
        
        # Check today's completions
        today_completions = TaskCompletion.get_today_completed(self.user)
        self.assertEqual(today_completions.count(), 1)
        self.assertEqual(today_completions.first(), completion)

class TimerSessionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create default tasks
        DailyTask.get_default_tasks()
    
    def test_timer_session(self):
        # Create a timer session
        session = TimerSession.objects.create(user=self.user)
        
        # Set end time to simulate 45 minutes of work
        session.start_time = timezone.now() - timedelta(minutes=45)
        session.end_session()
        
        # Check that session ended correctly
        self.assertEqual(session.duration_minutes, 45)
        self.assertEqual(session.xp_earned, 45)
        
        # Check that user got XP
        self.assertEqual(self.user.profile.total_xp, 45)
        
        # Check that the "Do 40 minutes Good Work" task was completed
        good_work_task = DailyTask.objects.get(name='Do 40 minutes Good Work')
        self.assertTrue(
            TaskCompletion.objects.filter(
                user=self.user,
                task=good_work_task
            ).exists()
        )

class ExtraTaskModelTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='12345',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
    
    def test_extra_task_creation(self):
        # Create a task for specific user
        personal_task = ExtraTask.objects.create(
            name='Personal Task',
            description='Test Description',
            xp_reward=50,
            assigned_by=self.admin,
            target_user=self.user,
            is_global=False,
            stock=1
        )
        
        # Create a global task
        global_task = ExtraTask.objects.create(
            name='Global Task',
            description='Test Description',
            xp_reward=30,
            assigned_by=self.admin,
            is_global=True,
            stock=5
        )
        
        # Check availability
        self.assertTrue(personal_task.is_available_for(self.user))
        self.assertFalse(personal_task.is_available_for(self.admin))
        self.assertTrue(global_task.is_available_for(self.user))
        self.assertTrue(global_task.is_available_for(self.admin))
        
        # Complete task
        self.assertTrue(personal_task.complete_for_user(self.user))
        # Stock should be 0 now
        personal_task.refresh_from_db()
        self.assertEqual(personal_task.stock, 0)
        
        # Task should no longer be available
        self.assertFalse(personal_task.is_available_for(self.user))
        
        # User should have received XP
        self.assertEqual(self.user.profile.total_xp, 50)
