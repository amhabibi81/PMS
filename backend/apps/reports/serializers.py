from rest_framework import serializers


class StatusDistributionItemSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class ProgressPointSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    project_progress = serializers.FloatField()


class WorkloadItemSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    open_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()


class OverdueTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    title = serializers.CharField()
    assignee = serializers.CharField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    days_late = serializers.IntegerField()


class ProjectSummarySerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    title = serializers.CharField()
    progress = serializers.FloatField()
    total_tasks = serializers.IntegerField()
    done_tasks = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    at_risk = serializers.BooleanField()
    flag = serializers.CharField()
