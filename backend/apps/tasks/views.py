from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMembership

from .filters import TaskFilter
from .models import Task, TaskComment
from .permissions import CanAccessTask
from .serializers import (
    AttachmentSerializer,
    TaskCommentSerializer,
    TaskSerializer,
)
from . import services


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD + transition/progress + nested comments/attachments for tasks."""

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = TaskFilter
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "due_date", "priority")

    queryset = (
        Task.objects.select_related("project", "assignee", "reporter")
        .prefetch_related("comments", "attachments")
    )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return qs
        member_project_ids = ProjectMembership.objects.filter(user=user).values_list(
            "project_id", flat=True
        )
        return qs.filter(project_id__in=member_project_ids)

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        reporter = self.request.user
        if reporter.role != User.Role.ADMIN and not ProjectMembership.objects.filter(
            project=project, user=reporter, role=ProjectMembership.Role.MANAGER
        ).exists():
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only project managers can create tasks in this project.")
        fields = {
            k: v for k, v in serializer.validated_data.items()
            if k not in ("project", "reporter")
        }
        task = services.create_task(project=project, reporter=reporter, **fields)
        serializer.instance = task

    def perform_update(self, serializer):
        task = serializer.instance
        actor = self.request.user
        if actor.role != User.Role.ADMIN and not (
            ProjectMembership.objects.filter(
                project=task.project, user=actor, role=ProjectMembership.Role.MANAGER
            ).exists()
            or task.assignee_id == actor.id
        ):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only the project manager or assignee can edit this task.")
        updated = services.update_task(task=task, actor=actor, **serializer.validated_data)
        serializer.instance = updated

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanAccessTask])
    def transition(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Task.Status.choices):
            return Response(
                {"detail": f"Invalid status. Choose from: {list(dict(Task.Status.choices).keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            services.transition_status(task=task, actor=request.user, new_status=new_status)
        except DjangoValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanAccessTask])
    def progress(self, request, pk=None):
        task = self.get_object()
        raw = request.data.get("progress")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return Response(
                {"detail": "progress must be an integer 0-100."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (0 <= value <= 100):
            return Response(
                {"detail": "progress must be between 0 and 100."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        services.set_progress(task=task, actor=request.user, value=value)
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated, CanAccessTask])
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == "POST":
            ser = TaskCommentSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            comment = services.add_comment(
                task=task, author=request.user, body=ser.validated_data["body"]
            )
            return Response(TaskCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        comments = task.comments.select_related("author")
        return Response(TaskCommentSerializer(comments, many=True).data)

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated, CanAccessTask])
    def attachments(self, request, pk=None):
        task = self.get_object()
        if request.method == "POST":
            file = request.FILES.get("file")
            if not file:
                return Response(
                    {"detail": "file is required."}, status=status.HTTP_400_BAD_REQUEST
                )
            attachment = services.upload_attachment(task=task, user=request.user, file=file)
            return Response(AttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)
        attachments = task.attachments.select_related("uploaded_by")
        return Response(AttachmentSerializer(attachments, many=True).data)
