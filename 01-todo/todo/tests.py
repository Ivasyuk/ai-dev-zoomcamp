from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo


class TodoModelTest(TestCase):
    """Test cases for the Todo model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='Test TODO',
            description='Test description',
            priority='high',
            owner=self.user
        )
    
    def test_todo_creation(self):
        """Test that a TODO can be created with all fields."""
        self.assertEqual(self.todo.title, 'Test TODO')
        self.assertEqual(self.todo.description, 'Test description')
        self.assertEqual(self.todo.priority, 'high')
        self.assertEqual(self.todo.status, 'pending')
        self.assertEqual(self.todo.owner, self.user)
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)
    
    def test_todo_string_representation(self):
        """Test the string representation of TODO."""
        expected = f"{self.todo.title} (Pending)"
        self.assertEqual(str(self.todo), expected)
    
    def test_todo_default_values(self):
        """Test that default values are set correctly."""
        todo = Todo.objects.create(
            title='Default TODO',
            owner=self.user
        )
        self.assertEqual(todo.status, 'pending')
        self.assertEqual(todo.priority, 'medium')
        self.assertIsNone(todo.due_date)
        self.assertIsNone(todo.completed_at)
    
    def test_mark_as_completed(self):
        """Test marking a TODO as completed."""
        self.todo.mark_as_completed()
        self.assertEqual(self.todo.status, 'completed')
        self.assertIsNotNone(self.todo.completed_at)
    
    def test_is_overdue_with_past_due_date(self):
        """Test is_overdue returns True for past due dates."""
        past_date = timezone.now() - timedelta(days=1)
        self.todo.due_date = past_date
        self.todo.save()
        self.assertTrue(self.todo.is_overdue())
    
    def test_is_overdue_with_future_due_date(self):
        """Test is_overdue returns False for future due dates."""
        future_date = timezone.now() + timedelta(days=1)
        self.todo.due_date = future_date
        self.todo.save()
        self.assertFalse(self.todo.is_overdue())
    
    def test_is_overdue_for_completed_todo(self):
        """Test is_overdue returns False for completed TODOs even if overdue."""
        past_date = timezone.now() - timedelta(days=1)
        self.todo.due_date = past_date
        self.todo.mark_as_completed()
        self.assertFalse(self.todo.is_overdue())
    
    def test_is_overdue_without_due_date(self):
        """Test is_overdue returns False when no due date is set."""
        self.assertFalse(self.todo.is_overdue())


class TodoViewTest(TestCase):
    """Test cases for the Todo views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        self.todo1 = Todo.objects.create(
            title='User1 TODO',
            description='Description 1',
            priority='high',
            owner=self.user1
        )
        self.todo2 = Todo.objects.create(
            title='User2 TODO',
            description='Description 2',
            priority='low',
            owner=self.user2
        )
    
    def test_todo_list_requires_authentication(self):
        """Test that todo_list view requires authentication."""
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_todo_list_shows_only_user_todos(self):
        """Test that users only see their own TODOs."""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User1 TODO')
        self.assertNotContains(response, 'User2 TODO')
    
    def test_todo_list_filtering_by_status(self):
        """Test filtering TODOs by status."""
        self.client.login(username='user1', password='pass123')
        self.todo1.status = 'completed'
        self.todo1.save()
        
        response = self.client.get(reverse('todo_list') + '?status=completed')
        self.assertEqual(response.status_code, 200)
        self.assertIn('todos', response.context)
        self.assertEqual(response.context['todos'].count(), 1)
    
    def test_todo_detail_view(self):
        """Test the todo_detail view."""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('todo_detail', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User1 TODO')
    
    def test_todo_detail_user_isolation(self):
        """Test that users cannot access other users' TODOs."""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('todo_detail', args=[self.todo2.pk]))
        self.assertEqual(response.status_code, 404)
    
    def test_todo_create_get(self):
        """Test GET request to todo_create view."""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_todo_create_post_valid(self):
        """Test creating a TODO with valid data."""
        self.client.login(username='user1', password='pass123')
        data = {
            'title': 'New TODO',
            'description': 'New description',
            'priority': 'medium',
        }
        response = self.client.post(reverse('todo_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Todo.objects.filter(title='New TODO').exists())
    
    def test_todo_create_post_without_title(self):
        """Test that creating TODO without title fails."""
        self.client.login(username='user1', password='pass123')
        data = {
            'description': 'No title',
            'priority': 'low',
        }
        initial_count = Todo.objects.count()
        response = self.client.post(reverse('todo_create'), data)
        # Should stay on the same page with error
        self.assertEqual(Todo.objects.count(), initial_count)
    
    def test_todo_update_view(self):
        """Test updating a TODO."""
        self.client.login(username='user1', password='pass123')
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
            'status': 'in_progress',
            'priority': 'high',
        }
        response = self.client.post(
            reverse('todo_update', args=[self.todo1.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated TODO')
        self.assertEqual(self.todo1.status, 'in_progress')
    
    def test_todo_delete_view(self):
        """Test deleting a TODO."""
        self.client.login(username='user1', password='pass123')
        todo_pk = self.todo1.pk
        response = self.client.post(reverse('todo_delete', args=[todo_pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=todo_pk).exists())
    
    def test_todo_complete_view(self):
        """Test marking a TODO as completed."""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('todo_complete', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 302)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, 'completed')
        self.assertIsNotNone(self.todo1.completed_at)
    
    def test_todo_stats_view(self):
        """Test the statistics view."""
        self.client.login(username='user1', password='pass123')
        # Create more TODOs for stats
        Todo.objects.create(
            title='Completed TODO',
            status='completed',
            owner=self.user1
        )
        Todo.objects.create(
            title='High Priority TODO',
            priority='high',
            owner=self.user1
        )
        
        response = self.client.get(reverse('todo_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.context)
        stats = response.context['stats']
        self.assertGreaterEqual(stats['total'], 3)
        self.assertGreaterEqual(stats['completed'], 1)
        self.assertGreaterEqual(stats['high_priority'], 2)
