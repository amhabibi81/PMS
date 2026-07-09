"""Notification helpers. Email sending is architecture-only (stubbed)."""
from .models import Notification


def notify_task_assigned(*, recipient, task):
    return Notification.objects.create(
        recipient=recipient,
        task=task,
        type=Notification.Type.TASK_ASSIGNED,
        message=f"You were assigned to: {task.title}",
    )


def notify_due_soon(*, recipient, task):
    return Notification.objects.create(
        recipient=recipient,
        task=task,
        type=Notification.Type.DUE_SOON,
        message=f"Task due soon: {task.title}",
    )


def notify_overdue(*, recipient, task):
    return Notification.objects.create(
        recipient=recipient,
        task=task,
        type=Notification.Type.OVERDUE,
        message=f"Task overdue: {task.title}",
    )
