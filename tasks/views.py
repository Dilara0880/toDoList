from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task, TaskPermission
from .serializers import TaskSerializer, TaskPermissionSerializer
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrReadOnly]


# class TaskAssignView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, task_id):
#         task = get_object_or_404(Task, id=task_id, owner=request.user)
#         user_id = request.data.get('user_id')
#         user = get_object_or_404(User, id=user_id)
#         task.assigned_to = user
#         task.save()
#         return Response({'status': 'task assigned'})

class TaskAssignView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if task.owner != request.user:
            return Response({"detail": "You do not have permission to assign permissions for this task."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user')
        permission_type = request.data.get('permission_type')

        if not user_id or not permission_type:
            return Response({"detail": "User ID and permission type are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if permission_type not in ['read', 'update']:
            return Response({"detail": "Invalid permission type."}, status=status.HTTP_400_BAD_REQUEST)

        permission, created = TaskPermission.objects.get_or_create(
            task=task,
            user=user,
            defaults={'permission_type': permission_type}
        )

        if not created:
            permission.permission_type = permission_type
            permission.save()

        serializer = TaskPermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if task.owner != request.user:
            return Response({"detail": "You do not have permission to remove permissions for this task."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user')
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        try:
            permission = TaskPermission.objects.get(task=task, user=user)
            permission.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TaskPermission.DoesNotExist:
            return Response({"detail": "Permission not found."}, status=status.HTTP_404_NOT_FOUND)