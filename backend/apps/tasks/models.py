from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.projects.models import Project


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "Todo", _("Todo")
        IN_PROGRESS = "InProgress", _("In Progress")
        REVIEW = "Review", _("Review")
        DONE = "Done", _("Done")

    class Priority(models.TextChoices):
        LOW = "Low", _("Low")
        MEDIUM = "Medium", _("Medium")
        HIGH = "High", _("High")
        URGENT = "Urgent", _("Urgent")

    # Allowed status transitions; enforced in services.py.
    # Done is reachable only via Review (or from InProgress -> Review -> Done).
    TRANSITIONS: dict[str, list[str]] = {
        Status.TODO: [Status.IN_PROGRESS],
        Status.IN_PROGRESS: [Status.REVIEW, Status.TODO],
        Status.REVIEW: [Status.DONE, Status.IN_PROGRESS],
        Status.DONE: [Status.IN_PROGRESS],  # reopen
    }

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="tasks"
    )
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.TODO
    )
    priority = models.CharField(
        _("priority"), max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    progress = models.PositiveSmallIntegerField(
        _("progress"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_tasks",
        null=True,
        blank=True,
        verbose_name=_("assignee"),
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_tasks",
        verbose_name=_("reporter"),
    )
    due_date = models.DateField(_("due date"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["assignee"]),
            models.Index(fields=["due_date"]),
        ]
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.TRANSITIONS.get(self.status, [])


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="comments"
    )
    body = models.TextField(_("body"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.task}"


def attachment_upload_path(instance, filename: str) -> str:
    return f"attachments/{instance.task_id}/{filename}"


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="attachments"
    )
    file = models.FileField(_("file"), upload_to=attachment_upload_path)
    filename = models.CharField(_("filename"), max_length=255)
    size = models.BigIntegerField(_("size in bytes"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self) -> str:
        return self.filename
