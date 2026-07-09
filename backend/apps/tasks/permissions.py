from rest_framework import permissions

from apps.projects.models import ProjectMembership


class CanAccessTask(permissions.BasePermission):
    """Read: project member. Write (create/update): project manager (or assignee for own task)."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "Admin":
            return True
        is_member = ProjectMembership.objects.filter(project=obj.project, user=user).exists()
        if request.method in permissions.SAFE_METHODS:
            return is_member
        if not is_member:
            return False
        is_manager = ProjectMembership.objects.filter(
            project=obj.project, user=user, role=ProjectMembership.Role.MANAGER
        ).exists()
        if is_manager:
            return True
        return obj.assignee_id == user.id
