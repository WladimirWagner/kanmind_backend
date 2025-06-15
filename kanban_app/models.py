from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    """
    Represents a Kanban board with tasks and members.
    Tracks various task counts for dashboard statistics.
    """
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='boards')
    ticket_count = models.IntegerField(default=0)
    task_to_do_count = models.IntegerField(default=0)
    task_high_prio_count = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')

    def member_count(self):
        return self.members.count()


class Task(models.Model):
    """
    Represents a task in a Kanban board.
    Includes status tracking, priority levels, and assignment details.
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_tasks')
    due_date = models.DateField()


class Comment(models.Model):
    """
    Represents a comment on a task.
    Includes timestamps for creation and updates.
    """
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']