"""Task business logic: creation, status transitions, progress, comments, attachments.

All transition/progress rules are enforced HERE (django-api skill), never in views.
"""
from django.core.exceptions import ValidationError

from apps.projects.services import log_activity
from apps.projects.models import ActivityLog, Project, ProjectMembership

from .models import Attachment, Task, TaskComment


class TransitionError(ValidationError):
    """Illegal task status transition."""


def create_task(*, project, reporter, **fields):
    task = Task.objects.create(project=project, reporter=reporter, **fields)
    log_activity(
        reporter, ActivityLog.Verb.TASK_CREATED, project,
        target_type="Task", target_id=task.id,
        metadata={"title": task.title, "assignee_id": task.assignee_id},
    )
    return task


def update_task(*, task, actor, **fields):
    assignee_changed = "assignee" in fields and fields["assignee"] != task.assignee
    for k, v in fields.items():
        setattr(task, k, v)
    task.save()
    log_activity(
        actor, ActivityLog.Verb.TASK_UPDATED, task.project,
        target_type="Task", target_id=task.id,
        metadata={k: str(v) for k, v in fields.items()},
    )
    if assignee_changed and task.assignee_id:
        log_activity(
            actor, ActivityLog.Verb.TASK_ASSIGNED, task.project,
            target_type="Task", target_id=task.id,
            metadata={"assignee_id": task.assignee_id},
        )
    return task


def transition_status(*, task, actor, new_status):
    """Enforce Todo -> InProgress -> Review -> Done (+ reopen Done -> InProgress)."""
    if not task.can_transition_to(new_status):
        raise TransitionError(
            f"Illegal status transition: {task.status} -> {new_status}. "
            f"Allowed: {task.TRANSITIONS.get(task.status, [])}"
        )
    old_status = task.status
    task.status = new_status
    # Setting status to Done forces progress = 100 (FR-3.4).
    if new_status == Task.Status.DONE and task.progress != 100:
        task.progress = 100
    task.save()
    log_activity(
        actor, ActivityLog.Verb.TASK_STATUS_CHANGED, task.project,
        target_type="Task", target_id=task.id,
        metadata={"from": old_status, "to": new_status},
    )
    return task


def set_progress(*, task, actor, value):
    """Manual 0-100. Locked at 100 if task is Done."""
    if task.status == Task.Status.DONE:
        value = 100
    task.progress = value
    task.save()
    log_activity(
        actor, ActivityLog.Verb.TASK_PROGRESS_CHANGED, task.project,
        target_type="Task", target_id=task.id,
        metadata={
            "task_id": task.id,
            "task_progress": value,
            "project_progress": task.project.progress,
        },
    )
    return task


def add_comment(*, task, author, body):
    comment = TaskComment.objects.create(task=task, author=author, body=body)
    log_activity(
        author, ActivityLog.Verb.COMMENT_ADDED, task.project,
        target_type="Task", target_id=task.id,
        metadata={"comment_id": comment.id},
    )
    return comment


def upload_attachment(*, task, user, file):
    attachment = Attachment.objects.create(
        task=task,
        uploaded_by=user,
        file=file,
        filename=file.name,
        size=file.size,
    )
    log_activity(
        user, ActivityLog.Verb.ATTACHMENT_UPLOADED, task.project,
        target_type="Task", target_id=task.id,
        metadata={"attachment_id": attachment.id, "filename": attachment.filename},
    )
    return attachment
