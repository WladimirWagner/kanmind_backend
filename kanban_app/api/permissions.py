from rest_framework import permissions

class IsBoardMemberOrOwner(permissions.BasePermission):
    """
    Allows access only to board members or the board owner.
    Used for read operations on boards.
    """
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user or request.user in obj.members.all():
            return True
        raise permissions.PermissionDenied("You must be either a member or the owner of this board.")


class IsBoardOwner(permissions.BasePermission):
    """
    Allows access only to the board owner.
    Used for write operations on boards.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Allows access only to the task creator or board owner.
    Used for task deletion.
    """
    def has_object_permission(self, request, view, obj):
      return obj.owner == request.user


class IsCommentCreator(permissions.BasePermission):
    """
    Allows access only to the comment creator.
    Used for comment modification and deletion.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user