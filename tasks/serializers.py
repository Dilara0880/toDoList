from rest_framework import serializers
from .models import Task, TaskPermission
from accounts.serializers import UserSerializer



class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'assigned_to']

class TaskPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPermission
        fields = ['id', 'task', 'user', 'permission_type']
        extra_kwargs = {
            'task': {'read_only': True},
            'user': {'read_only': True}
        }