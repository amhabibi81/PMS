from django.contrib import admin

from .models import Attachment, Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "assignee",
        "reporter",
        "status",
        "priority",
        "progress",
        "due_date",
    )
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    autocomplete_fields = ("project", "assignee", "reporter")


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("body",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("filename", "task", "uploaded_by", "size", "created_at")
    readonly_fields = ("size",)
