from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True, default="")

    class Meta:
        model = Notification
        fields = ("id", "recipient", "task", "task_title", "type", "message", "is_read", "created_at")
        read_only_fields = ("id", "recipient", "task", "type", "message", "created_at")
