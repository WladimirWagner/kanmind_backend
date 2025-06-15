from rest_framework import generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import Http404

from ..models import Board, Task, Comment, User
from .serializers import *
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsTaskCreatorOrBoardOwner, IsCommentCreator


# Board Views
class BoardListCreateView(generics.ListCreateAPIView):
    """
    View for listing all boards and creating new boards.
    Users can only see boards they own or are members of.
    
    GET: Returns a list of all boards where the user is either the owner or a member.
    POST: Creates a new board with the authenticated user as owner.
         Required fields:
         - title: The title of the board
         Optional fields:
         - members: List of user IDs to be added as board members
    """
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        title = self.request.data.get("title")
        members_ids = self.request.data.get("members", [])

        if not title:
            raise serializers.ValidationError({'error': 'Title is required'})

        board = serializer.save(owner=self.request.user)
        board.members.set(members_ids)
        return board


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting a specific board.
    Only board owners can update or delete boards.
    
    GET: Returns detailed information about a specific board
    PATCH: Updates board title and members
           - Only board owners can modify the board
           - Can update title and members list
           - Members not included in the request will be removed
    DELETE: Removes the board
           - Only board owners can delete the board
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'board_id'

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_object(self):
        try:
            board = Board.objects.get(pk=self.kwargs['board_id'])
            
            # Prüfe Berechtigungen basierend auf der HTTP-Methode
            if self.request.method in ['PUT', 'PATCH', 'DELETE']:
                if board.owner != self.request.user:
                    raise permissions.PermissionDenied("Only the board owner can modify or delete the board.")
            else:  # GET
                if not (board.owner == self.request.user or self.request.user in board.members.all()):
                    raise permissions.PermissionDenied("You must be either a member or the owner of this board.")
            
            return board
        except Board.DoesNotExist:
            raise Http404("Board not found")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        members_ids = request.data.pop('members', None)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if members_ids is not None:
            instance.members.set(members_ids)

        return Response(serializer.data)


# Email Check View
class EmailCheckView(generics.RetrieveAPIView):
    """
    View for checking if an email address is already registered.
    Returns user information if the email exists.
    
    GET: Checks if an email address is registered in the system
         Query Parameters:
         - email: The email address to check
         Returns:
         - User information if email exists
         - 404 if email not found
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserShortSerializer

    def get_object(self):
        email = self.request.query_params.get('email')
        if not email:
            raise serializers.ValidationError({'error': 'Email parameter is required'})

        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            raise Http404("No user found with this email address")


# Task Views
class TaskCreateView(generics.CreateAPIView):
    """
    View for creating new tasks.
    Validates board membership and assignee/reviewer permissions.
    
    POST: Creates a new task on a board
          Required fields:
          - board: ID of the board to create the task in
          Optional fields:
          - assignee_id: ID of the user to assign the task to
          - reviewer_id: ID of the user to review the task
          Validates:
          - User must be board owner or member
          - Assignee and reviewer must be board members
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        board_id = self.request.data.get('board')
        if not board_id:
            raise serializers.ValidationError({'error': 'board is required'})

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise Http404("Board not found")

        # Prüfe Board-Mitgliedschaft
        if not (board.owner == self.request.user or self.request.user in board.members.all()):
            raise permissions.PermissionDenied("You must be a member of the board to create tasks.")

        # Check if assignee and reviewer are board members
        assignee_id = self.request.data.get('assignee_id')
        reviewer_id = self.request.data.get('reviewer_id')

        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
                if not (assignee == board.owner or assignee in board.members.all()):
                    raise serializers.ValidationError({'error': 'Assignee must be a member of the board'})
            except User.DoesNotExist:
                raise serializers.ValidationError({'error': 'Assignee not found'})

        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
                if not (reviewer == board.owner or reviewer in board.members.all()):
                    raise serializers.ValidationError({'error': 'Reviewer must be a member of the board'})
            except User.DoesNotExist:
                raise serializers.ValidationError({'error': 'Reviewer not found'})

        serializer.save(board=board)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting specific tasks.
    Only board owners can delete tasks.
    
    GET: Returns detailed information about a specific task
    PATCH: Updates task information
           - Board members can update task details
           - Validates assignee and reviewer are board members
    DELETE: Removes the task
            - Only board owners can delete tasks
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMemberOrOwner]
    lookup_url_kwarg = 'task_id'

    def get_queryset(self):
        return Task.objects.all()

    def get_object(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        self.check_object_permissions(self.request, task.board)
        return task

    def get_permissions(self):
        if self.request.method in ['PATCH']:
            return [permissions.IsAuthenticated(), IsBoardMemberOrOwner()]
        elif self.request.method in ['DELETE']:
            return [permissions.IsAuthenticated(), IsBoardOwner()]
        return [permissions.IsAuthenticated(), IsBoardMemberOrOwner()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        board = instance.board

        # Check if assignee and reviewer are board members
        assignee_id = request.data.get('assignee_id')
        reviewer_id = request.data.get('reviewer_id')

        if assignee_id:
            assignee = get_object_or_404(User, id=assignee_id)
            if not (assignee == board.owner or assignee in board.members.all()):
                raise serializers.ValidationError({'error': 'Assignee must be a member of the board'})

        if reviewer_id:
            reviewer = get_object_or_404(User, id=reviewer_id)
            if not (reviewer == board.owner or reviewer in board.members.all()):
                raise serializers.ValidationError({'error': 'Reviewer must be a member of the board'})

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class TaskAssignedToMeView(generics.ListAPIView):
    """
    View for listing tasks assigned to the current user.
    Returns all tasks where the user is the assignee.
    
    GET: Returns a list of all tasks where the authenticated user is the assignee
         - Includes task details and related board information
         - Tasks are returned in chronological order
    """
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class TaskReviewingView(generics.ListAPIView):
    """
    View for listing tasks that need review by the current user.
    Returns all tasks where the user is the reviewer.
    
    GET: Returns a list of all tasks where the authenticated user is the reviewer
         - Includes task details and related board information
         - Tasks are returned in chronological order
    """
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating comments on a specific task.
    Only board members can view and create comments.
    
    GET: Returns all comments for a specific task
         - Comments are returned in chronological order
         - Only accessible to board members
    POST: Creates a new comment on a task
          Required fields:
          - content: The comment text
          - Only board members can create comments
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise Http404("Task not found")

        if not (task.board.owner == self.request.user or self.request.user in task.board.members.all()):
            raise permissions.PermissionDenied("You don't have permission to view comments for this task.")
        
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise Http404("Task not found")

        if not (task.board.owner == self.request.user or self.request.user in task.board.members.all()):
            raise permissions.PermissionDenied("You don't have permission to create comments for this task.")
        
        serializer.save(author=self.request.user, task=task)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting specific comments.
    Only comment authors can modify or delete their comments.
    
    GET: Returns detailed information about a specific comment
    PUT/PATCH: Updates comment content
               - Only the comment author can modify the comment
    DELETE: Removes the comment
            - Only the comment author can delete the comment
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentCreator]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'], task_id=self.kwargs['task_id'])
        self.check_object_permissions(self.request, comment)
        return comment



