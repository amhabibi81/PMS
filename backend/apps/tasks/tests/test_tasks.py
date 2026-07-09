import pytest

from apps.projects.models import ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory


@pytest.mark.django_db
def test_member_cannot_create_task(authed_client, member_user):
    p = ProjectFactory()
    ProjectMembership.objects.create(project=p, user=member_user)
    resp = authed_client(member_user).post("/api/v1/tasks/", {
        "project": p.id, "title": "T",
    }, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_pm_creates_task(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    resp = authed_client(pm_user).post("/api/v1/tasks/", {
        "project": p.id, "title": "New task",
    }, format="json")
    assert resp.status_code == 201, resp.data
    assert resp.data["title"] == "New task"


@pytest.mark.django_db
def test_illegal_transition_rejected_with_400(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    t = TaskFactory(project=p, status=Task.Status.TODO)
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/transition/", {"status": "Done"}, format="json"
    )
    assert resp.status_code == 400
    assert "Illegal" in resp.data["detail"]


@pytest.mark.django_db
def test_legal_transition_succeeds(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    t = TaskFactory(project=p, status=Task.Status.TODO)
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/transition/", {"status": "InProgress"}, format="json"
    )
    assert resp.status_code == 200, resp.data
    t.refresh_from_db()
    assert t.status == Task.Status.IN_PROGRESS


@pytest.mark.django_db
def test_done_status_forces_progress_100(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    t = TaskFactory(project=p, status=Task.Status.REVIEW, progress=30)
    authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/transition/", {"status": "Done"}, format="json"
    )
    t.refresh_from_db()
    assert t.progress == 100


@pytest.mark.django_db
def test_progress_out_of_range_rejected(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    t = TaskFactory(project=p)
    resp = authed_client(pm_user).post(
        f"/api/v1/tasks/{t.id}/progress/", {"progress": 150}, format="json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_assignee_can_comment(authed_client, member_user):
    p = ProjectFactory()
    ProjectMembership.objects.create(project=p, user=member_user)
    t = TaskFactory(project=p, assignee=member_user)
    resp = authed_client(member_user).post(
        f"/api/v1/tasks/{t.id}/comments/", {"body": "Hello"}, format="json"
    )
    assert resp.status_code == 201, resp.data
    assert resp.data["body"] == "Hello"


@pytest.mark.django_db
def test_non_member_cannot_see_task(authed_client, member_user):
    p = ProjectFactory()
    t = TaskFactory(project=p)
    resp = authed_client(member_user).get(f"/api/v1/tasks/{t.id}/")
    assert resp.status_code == 404
