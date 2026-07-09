from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "Planning", _("Planning")
        ACTIVE = "Active", _("Active")
        ON_HOLD = "OnHold", _("On Hold")
        COMPLETED = "Completed", _("Completed")
        ARCHIVED = "Archived", _("Archived")

    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    start_date = models.DateField(_("start date"))
    due_date = models.DateField(_("due date"), null=True, blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.PLANNING
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"])]
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self) -> str:
        return self.title

    @property
    def progress(self) -> float:
        """Computed project progress = average of task progress.

        Never stored denormalized (db-design rule); source of truth is Task.progress.
        """
        agg = self.tasks.aggregate(avg=models.Avg("progress"))
        return round(agg["avg"] or 0, 2)


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        MANAGER = "Manager", _("Manager")
        MEMBER = "Member", _("Member")

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(
        _("role"), max_length=20, choices=Role.choices, default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_project_membership"
            )
        ]
        indexes = [models.Index(fields=["project", "user"])]
        verbose_name = _("project membership")
        verbose_name_plural = _("project memberships")

    def __str__(self) -> str:
        return f"{self.user} @ {self.project} ({self.role})"


class ActivityLog(models.Model):
    """Append-only audit/event log.

    Powers the activity feed and the project progress-over-time report.
    Target is polymorphic but modeled simply as (target_type, target_id)
    instead of contenttypes — simpler to explain and defend in the thesis.
    A direct project FK is kept for fast per-project filtering (indexed).
    """

    class Verb(models.TextChoices):
        PROJECT_CREATED = "PROJECT_CREATED", _("Project created")
        PROJECT_UPDATED = "PROJECT_UPDATED", _("Project updated")
        MEMBER_ADDED = "MEMBER_ADDED", _("Member added")
        MEMBER_REMOVED = "MEMBER_REMOVED", _("Member removed")
        TASK_CREATED = "TASK_CREATED", _("Task created")
        TASK_UPDATED = "TASK_UPDATED", _("Task updated")
        TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED", _("Task status changed")
        TASK_PROGRESS_CHANGED = "TASK_PROGRESS_CHANGED", _("Task progress changed")
        TASK_ASSIGNED = "TASK_ASSIGNED", _("Task assigned")
        COMMENT_ADDED = "COMMENT_ADDED", _("Comment added")
        ATTACHMENT_UPLOADED = "ATTACHMENT_UPLOADED", _("Attachment uploaded")

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="activity_logs",
        null=True,
        blank=True,
        verbose_name=_("project"),
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="activity_logs",
        verbose_name=_("actor"),
    )
    verb = models.CharField(_("verb"), max_length=30, choices=Verb.choices)
    target_type = models.CharField(_("target type"), max_length=30)
    target_id = models.BigIntegerField(_("target id"), null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "created_at"]),
            models.Index(fields=["verb", "created_at"]),
        ]
        verbose_name = _("activity log")
        verbose_name_plural = _("activity logs")

    def __str__(self) -> str:
        return f"{self.actor} {self.verb} {self.target_type}:{self.target_id} @ {self.created_at:%Y-%m-%d %H:%M}"
