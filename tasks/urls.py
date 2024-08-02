from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskAssignView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list'),
    path('create/', TaskListCreateView.as_view(), name='create-task'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/assign/', TaskAssignView.as_view(), name='task-assign'),
    path('<int:task_id>/permissions/', TaskAssignView.as_view(), name='task-permission-manage'),
]
