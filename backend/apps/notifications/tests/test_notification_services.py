import pytest

from apps.accounts.tests.factories import UserFactory
from apps.notifications import services
from apps.notifications.models import Notification
from apps.projects.tests.factories import ProjectFactory
from apps.tasks.tests.factories import TaskFactory


@pytest.mark.django_db
def test_notify_task_assigned_creates_notification():
    user = UserFactory()
    task = TaskFactory(assignee=user)
    n = services.notify_task_assigned(recipient=user, task=task)
    assert n.type == Notification.Type.TASK_ASSIGNED
    assert n.recipient_id == user.id


@pytest.mark.django_db
def test_notify_due_soon_and_overdue():
    user = UserFactory()
    task = TaskFactory(assignee=user)
    a = services.notify_due_soon(recipient=user, task=task)
    b = services.notify_overdue(recipient=user, task=task)
    assert a.type == Notification.Type.DUE_SOON
    assert b.type == Notification.Type.OVERDUE
