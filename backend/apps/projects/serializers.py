from django.conf import settings
from rest_framework import serializers

from apps.accounts.models import User

from .models import ActivityLog, Project, ProjectMembership


class ProjectMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(choices=ProjectMembership.Role.choices)

    class Meta:
        model = ProjectMembership
        fields = ("id", "project", "user", "username", "role", "joined_at")
        read_only_fields = ("id", "project", "joined_at", "username")


class ProjectSerializer(serializers.ModelSerializer):
    progress = serializers.FloatField(read_only=True)
    members_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id", "title", "description", "start_date", "due_date", "status",
            "created_by", "progress", "members_count", "tasks_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_by", "progress", "created_at", "updated_at")

    def get_members_count(self, obj):
        return obj.memberships.count()

    def get_tasks_count(self, obj):
        return obj.tasks.count()


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = ActivityLog
        fields = (
            "id", "project", "actor", "verb", "target_type",
            "target_id", "metadata", "created_at",
        )
        read_only_fields = fields
