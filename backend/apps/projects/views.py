from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import IsProjectManagerOrAdmin

from .filters import ProjectFilter
from .models import ActivityLog, Project, ProjectMembership
from .permissions import IsProjectManager, IsProjectMember
from .serializers import (
    ActivityLogSerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
)
from . import services


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for projects.

    - list: Admin sees all; others see projects they're a member of.
    - create: PM/Admin only.
    - read/update/delete: members read; project managers write.
    """

    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = ProjectFilter
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "due_date", "title")
    queryset = Project.objects.select_related("created_by").prefetch_related(
        "memberships", "tasks"
    )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return qs
        return qs.filter(memberships__user=user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsProjectManagerOrAdmin()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsProjectMember(), IsProjectManager()]
        return [IsAuthenticated(), IsProjectMember()] if self.action == "retrieve" else [
            IsAuthenticated()
        ]

    def perform_create(self, serializer):
        project = services.create_project(actor=self.request.user, **serializer.validated_data)
        serializer.instance = project

    def perform_update(self, serializer):
        project = services.update_project(
            project=serializer.instance, actor=self.request.user, **serializer.validated_data
        )
        serializer.instance = project

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated, IsProjectMember])
    def members(self, request, pk=None):
        project = self.get_object()
        if request.method == "POST":
            self.check_object_permissions(request, project)
            if not (
                request.user.role == User.Role.ADMIN
                or ProjectMembership.objects.filter(
                    project=project, user=request.user, role=ProjectMembership.Role.MANAGER
                ).exists()
            ):
                return Response(
                    {"detail": "Only project managers can add members."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            ser = ProjectMembershipSerializer(
                data=request.data, context={"request": request}
            )
            ser.is_valid(raise_exception=True)
            membership = services.add_member(
                project=project,
                actor=request.user,
                user=ser.validated_data["user"],
                role=ser.validated_data["role"],
            )
            return Response(ProjectMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)
        memberships = project.memberships.select_related("user")
        return Response(ProjectMembershipSerializer(memberships, many=True).data)

    @action(
        detail=True, methods=["delete"],
        permission_classes=[IsAuthenticated, IsProjectMember],
        url_path=r"members/(?P<user_id>\d+)",
    )
    def remove_member(self, request, pk=None, user_id=None):
        project = self.get_object()
        target = get_object_or_404(User, pk=user_id)
        if not (
            request.user.role == User.Role.ADMIN
            or ProjectMembership.objects.filter(
                project=project, user=request.user, role=ProjectMembership.Role.MANAGER
            ).exists()
        ):
            return Response(
                {"detail": "Only project managers can remove members."},
                status=status.HTTP_403_FORBIDDEN,
            )
        deleted = services.remove_member(project=project, actor=request.user, user=target)
        if not deleted:
            return Response({"detail": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsProjectMember])
    def activity(self, request, pk=None):
        project = self.get_object()
        logs = project.activity_logs.select_related("actor")[:100]
        return Response(ActivityLogSerializer(logs, many=True).data)
