from django.urls import path
from . import views

urlpatterns = [
    path('boards/', views.BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:board_id>/', views.BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', views.TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', views.CommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('tasks/assigned-to-me/', views.TaskAssignedToMeView.as_view(), name='tasks-assigned'),
    path('tasks/reviewing/', views.TaskReviewingView.as_view(), name='tasks-reviewing'),
    path('email-check/', views.EmailCheckView.as_view(), name='email-check'),
]
