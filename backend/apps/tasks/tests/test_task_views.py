"""Extra coverage for tasks views: update, progress validation, comments list, attachments."""
import pytest

from apps.projects.models import ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory


def _setup(pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    return p


@pytest.mark.django_db
def test_pm_updates_task_fields(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p)
    resp = authed_client(pm_user).patch(
        f"/api/v1/tasks/{t.id}/", {"title": "Renamed", "priority": "High"}, format="json"
    )
    assert resp.status_code == 200, resp.data
    t.refresh_from_db()
    assert t.title == "Renamed"
    assert t.priority == Task.Priority.HIGH


@pytest.mark.django_db
def test_assignee_can_update_own_task(authed_client, member_user):
    p = _setup_via_member(member_user)
    t = TaskFactory(project=p, assignee=member_user)
    resp = authed_client(member_user).patch(
        f"/api/v1/tasks/{t.id}/", {"title": "By assignee"}, format="json"
    )
    assert resp.status_code == 200


def _setup_via_member(member_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=member_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    return p


@pytest.mark.django_db
def test_transition_invalid_status_returns_400(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p)
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/transition/", {"status": "Bogus"}, format="json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_progress_non_integer_returns_400(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p)
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/progress/", {"progress": "abc"}, format="json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_comments_list_get(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p)
    authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/comments/", {"body": "first"}, format="json"
    )
    resp = authed_client(pm_user).get(f"/api/v1/tasks/{t.id}/comments/")
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_attachment_upload_requires_file(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p)
    resp = authed_client(pm_user).post(f"/api/v1/tasks/{t.id}/attachments/")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_attachment_upload_success(authed_client, pm_user):
    from django.core.files.uploadedfile import SimpleUploadedFile

    p = _setup(pm_user)
    t = TaskFactory(project=p)
    f = SimpleUploadedFile("notes.txt", b"abc", content_type="text/plain")
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/attachments/", {"file": f}, format="multipart"
    )
    assert resp.status_code == 201, resp.data
    assert resp.data["filename"] == "notes.txt"
    assert resp.data["size"] == 3


@pytest.mark.django_db
def test_task_list_filters_by_status(authed_client, pm_user):
    p = _setup(pm_user)
    TaskFactory(project=p, status=Task.Status.TODO)
    TaskFactory(project=p, status=Task.Status.DONE)
    resp = authed_client(pm_user).get("/api/v1/tasks/?status=Done")
    assert resp.status_code == 200
    assert all(r["status"] == "Done" for r in resp.data["results"])
