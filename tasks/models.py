from django.db import models
from django.contrib.auth import get_user_model
from toDoList import settings

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')


class TaskPermission(models.Model):
    PERMISSION_CHOICES = (
        ('read', 'Read'),
        ('update', 'Update'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_permissions')
    permission_type = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ('task', 'user', 'permission_type')
        constraints = [
            models.UniqueConstraint(fields=['task', 'user', 'permission_type'], name='unique_task_permission')
        ]

    def __str__(self):
        return f"{self.user} - {self.task.title} - {self.permission_type}"
