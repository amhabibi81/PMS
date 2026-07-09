from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Task


class Notification(models.Model):
    class Type(models.TextChoices):
        TASK_ASSIGNED = "TASK_ASSIGNED", _("Task Assigned")
        DUE_SOON = "DUE_SOON", _("Due Soon")
        OVERDUE = "OVERDUE", _("Overdue")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    type = models.CharField(_("type"), max_length=20, choices=Type.choices)
    message = models.TextField(_("message"))
    is_read = models.BooleanField(_("is read"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "created_at"]),
        ]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self) -> str:
        return f"{self.type} -> {self.recipient}"
