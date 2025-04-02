from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import DailyTask, ExtraTask, GoodWorkSession
from datetime import timedelta


class DailyTaskTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='taskuser',
            email='task@example.com',
            password='taskpassword'
        )
        
    def test_get_user_tasks(self):
        """Test that daily tasks are created for a user"""
        tasks = DailyTask.get_user_tasks(self.user)
        
        # Check that we have 3 default tasks
        self.assertEqual(tasks.count(), 3)
        
        # Check that calling again doesn't create duplicate tasks
        tasks2 = DailyTask.get_user_tasks(self.user)
        self.assertEqual(tasks2.count(), 3)
        
    def test_process_daily_tasks(self):
        """Test processing of daily tasks and XP rewards/penalties"""
        # Get tasks
        tasks = DailyTask.get_user_tasks(self.user)
        
        # Test case 1: No tasks completed (level 0, no penalty)
        completed, xp_change = DailyTask.process_daily_tasks(self.user)
        self.assertEqual(completed, 0)
        self.assertEqual(xp_change, 0)
        
        # Add some XP to level up
        self.user.profile.add_xp(10)
        self.assertEqual(self.user.profile.level, 1)
        
        # Test case 2: No tasks completed (level 1, should be penalized)
        completed, xp_change = DailyTask.process_daily_tasks(self.user)
        self.assertEqual(completed, 0)
        self.assertEqual(xp_change, -11)  # 10 + level
        
        # Reset profile XP
        self.user.profile.level = 0
        self.user.profile.total_xp = 0
        self.user.profile.current_xp = 0
        self.user.profile.save()
        
        # Test case 3: Complete 1 task (no reward or penalty)
        task = tasks.first()
        task.completed = True
        task.save()
        
        completed, xp_change = DailyTask.process_daily_tasks(self.user)
        self.assertEqual(completed, 1)
        self.assertEqual(xp_change, 0)
        
        # Test case 4: Complete 2 tasks (80 XP reward)
        task2 = tasks[1]
        task2.completed = True
        task2.save()
        
        completed, xp_change = DailyTask.process_daily_tasks(self.user)
        self.assertEqual(completed, 2)
        self.assertEqual(xp_change, 80)
        
        # Test case 5: Complete all 3 tasks (200 XP reward)
        task3 = tasks[2]
        task3.completed = True
        task3.save()
        
        completed, xp_change = DailyTask.process_daily_tasks(self.user)
        self.assertEqual(completed, 3)
        self.assertEqual(xp_change, 200)


class GoodWorkSessionTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='goodworkuser',
            email='goodwork@example.com',
            password='gwpassword'
        )
        
        # Create daily tasks
        DailyTask.get_user_tasks(self.user)
        
    def test_good_work_session(self):
        """Test good work session and XP earning"""
        # Create a session
        session = GoodWorkSession.objects.create(user=self.user)
        
        # Set end time to be 45 minutes later
        session.start_time = timezone.now() - timedelta(minutes=45)
        
        # End session
        xp_earned = session.end_session()
        
        # Check that XP was earned (should be 45)
        self.assertEqual(xp_earned, 45)
        self.assertEqual(session.duration_minutes, 45)
        
        # Check that user received XP
        self.assertEqual(self.user.profile.total_xp, 45)
        
        # Check that daily task was completed
        good_work_task = DailyTask.objects.get(
            user=self.user,
            title='good_work',
            date=timezone.now().date()
        )
        self.assertTrue(good_work_task.completed)
