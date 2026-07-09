from rest_framework import permissions

from .models import ProjectMembership


class IsProjectMember(permissions.BasePermission):
    """Read access requires project membership (or Admin)."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "Admin":
            return True
        return ProjectMembership.objects.filter(project=obj, user=user).exists()


class IsProjectManager(permissions.BasePermission):
    """Write access requires Project Manager role on that project (or Admin)."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "Admin":
            return True
        return ProjectMembership.objects.filter(
            project=obj, user=user, role=ProjectMembership.Role.MANAGER
        ).exists()


class ProjectMemberMixin:
    """Helper for nested resources under a project: load & permission-check the project."""

    def get_project(self):
        from django.shortcuts import get_object_or_404
        from .models import Project

        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        user = self.request.user
        if user.role != "Admin" and not ProjectMembership.objects.filter(
            project=project, user=user
        ).exists():
            self.permission_denied(self.request, message="Not a member of this project.")
        return project
