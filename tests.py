from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tasks.models import Task, TaskPermission

User = get_user_model()

class TaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.client.login(username='testuser', password='testpass')
        self.task = Task.objects.create(title='Test Task', description='Test Description', owner=self.user)

    def test_create_task(self):
        url = reverse('create-task')
        data = {'title': 'New Task', 'description': 'New Description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.get(id=3).title, 'New Task')

    def test_update_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        data = {'title': 'Updated Task', 'description': 'Updated Description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_delete_task(self):
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_assign_permission(self):
        url = reverse('task-assign', kwargs={'task_id': self.task.id})
        data = {'user': self.user2.id, 'permission_type': 'read'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TaskPermission.objects.count(), 1)
        self.assertEqual(TaskPermission.objects.get(id=1).user, self.user2)

    def test_remove_permission(self):
        TaskPermission.objects.create(task=self.task, user=self.user2, permission_type='read')
        url = reverse('task-permission-manage', kwargs={'task_id': self.task.id})
        data = {'user': self.user2.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaskPermission.objects.count(), 0)
