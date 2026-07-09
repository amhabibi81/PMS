from django.contrib import admin

from .models import ActivityLog, Project, ProjectMembership


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_by", "start_date", "due_date")
    list_filter = ("status",)
    search_fields = ("title", "description")
    date_hierarchy = "created_at"


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("project__title", "user__username")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "verb", "target_type", "target_id", "project", "created_at")
    list_filter = ("verb", "created_at")
    search_fields = ("actor__username", "project__title")
    readonly_fields = (
        "project",
        "actor",
        "verb",
        "target_type",
        "target_id",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
