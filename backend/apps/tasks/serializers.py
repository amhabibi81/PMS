from rest_framework import serializers

from apps.projects.models import Project, ProjectMembership
from apps.accounts.models import User

from .models import Attachment, Task, TaskComment


class TaskCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskComment
        fields = ("id", "task", "author", "body", "created_at", "updated_at")
        read_only_fields = ("id", "task", "author", "created_at", "updated_at")


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Attachment
        fields = ("id", "task", "uploaded_by", "file", "filename", "size", "created_at")
        read_only_fields = ("id", "task", "uploaded_by", "size", "created_at")


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True, required=False
    )
    reporter = serializers.StringRelatedField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Task
        fields = (
            "id", "project", "title", "description", "status", "priority",
            "progress", "assignee", "reporter", "due_date",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "reporter", "progress", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        project = attrs.get("project") or getattr(self.instance, "project", None)
        if project and request and request.user.role != "Admin":
            if not ProjectMembership.objects.filter(
                project=project, user=request.user
            ).exists():
                raise serializers.ValidationError(
                    {"project": "You are not a member of this project."}
                )
        assignee = attrs.get("assignee")
        if assignee and project and not ProjectMembership.objects.filter(
            project=project, user=assignee
        ).exists():
            raise serializers.ValidationError(
                {"assignee": "Assignee must be a member of the project."}
            )
        return attrs
