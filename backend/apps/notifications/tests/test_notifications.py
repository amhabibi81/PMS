import datetime as dt

import pytest

from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.projects.models import ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.tasks.tests.factories import TaskFactory


@pytest.mark.django_db
def test_list_own_notifications(authed_client, member_user, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.create(project=p, user=member_user)
    t = TaskFactory(project=p, assignee=member_user)
    Notification.objects.create(
        recipient=member_user, task=t, type=Notification.Type.TASK_ASSIGNED, message="x"
    )
    other = User.objects.create_user(username="o", email="o@pms.local", password="pass12345")
    Notification.objects.create(recipient=other, type=Notification.Type.OVERDUE, message="y")

    resp = authed_client(member_user).get("/api/v1/notifications/")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["type"] == Notification.Type.TASK_ASSIGNED


@pytest.mark.django_db
def test_mark_read(authed_client, member_user):
    n = Notification.objects.create(recipient=member_user, type=Notification.Type.OVERDUE, message="m")
    resp = authed_client(member_user).post(f"/api/v1/notifications/{n.id}/mark-read/")
    assert resp.status_code == 200
    n.refresh_from_db()
    assert n.is_read is True


@pytest.mark.django_db
def test_mark_all_read(authed_client, member_user):
    Notification.objects.create(recipient=member_user, type=Notification.Type.OVERDUE, message="1")
    Notification.objects.create(recipient=member_user, type=Notification.Type.DUE_SOON, message="2")
    resp = authed_client(member_user).post("/api/v1/notifications/mark-all-read/")
    assert resp.status_code == 200
    assert resp.data["marked_read"] == 2


@pytest.mark.django_db
def test_unread_filter(authed_client, member_user):
    Notification.objects.create(recipient=member_user, type=Notification.Type.OVERDUE, message="1", is_read=True)
    Notification.objects.create(recipient=member_user, type=Notification.Type.DUE_SOON, message="2")
    resp = authed_client(member_user).get("/api/v1/notifications/?unread=true")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
