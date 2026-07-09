from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdmin(BasePermission):
    """Global Admin role only."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsProjectManagerOrAdmin(BasePermission):
    """Global ProjectManager or Admin. Sufficient for creating projects."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_project_manager
        )


class IsAuthenticatedReadOnly(BasePermission):
    """Any authenticated user, read-only."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.method in SAFE_METHODS


class IsSelf(BasePermission):
    """Only the user themselves (used for /me)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj == request.user
