from rest_framework import serializers
from ..models import Board, Task, Comment
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    """
    Simplified user serializer for basic user information.
    Used in nested serializations.
    """
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    """
    Full task serializer with nested user information.
    Handles assignee and reviewer relationships.
    """
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'comments_count', 
            'priority', 'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'due_date'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        
        task = Task.objects.create(**validated_data)
        
        if assignee_id:
            task.assignee_id = assignee_id
        if reviewer_id:
            task.reviewer_id = reviewer_id
        
        task.save()
        return task

    def update(self, instance, validated_data):
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if assignee_id is not None:
            instance.assignee_id = assignee_id
        if reviewer_id is not None:
            instance.reviewer_id = reviewer_id
        
        instance.save()
        return instance


class BoardSerializer(serializers.ModelSerializer):
    """
    Basic board serializer for list views.
    Includes member count, ticket count, task to do count, and task high priority count.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    task_to_do_count = serializers.SerializerMethodField()
    task_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title','member_count', 'ticket_count', 'task_to_do_count', 'task_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_task_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()
    
    def get_task_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed board serializer with nested tasks and members.
    Used for board detail views.
    """
    owner_id = serializers.IntegerField(source='owner.id')
    members = UserShortSerializer(many=True)
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer with full name handling.
    Used in task list views.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'fullname')

    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username


class TaskListSerializer(serializers.ModelSerializer):
    """
    Simplified task serializer for list views.
    Includes basic task information and user details.
    """
    assignee = SimpleUserSerializer()
    reviewer = SimpleUserSerializer()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority', 
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment serializer with nested author information.
    Includes read-only timestamps.
    """
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']