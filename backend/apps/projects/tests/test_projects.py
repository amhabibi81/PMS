import pytest

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMembership
from apps.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
def test_member_cannot_create_project(authed_client, member_user):
    resp = authed_client(member_user).post("/api/v1/projects/", {"title": "X"}, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_pm_creates_project_and_becomes_manager(authed_client, pm_user):
    resp = authed_client(pm_user).post("/api/v1/projects/", {
        "title": "New Project", "start_date": "2026-01-01",
    }, format="json")
    assert resp.status_code == 201, resp.data
    assert resp.data["title"] == "New Project"
    assert ProjectMembership.objects.filter(
        project_id=resp.data["id"], user=pm_user, role=ProjectMembership.Role.MANAGER
    ).exists()


@pytest.mark.django_db
def test_member_sees_only_their_projects(authed_client, member_user, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.create(project=p, user=member_user)
    ProjectFactory()  # another project member_user is NOT in
    resp = authed_client(member_user).get("/api/v1/projects/")
    assert resp.status_code == 200
    project_ids = [row["id"] for row in resp.data["results"]]
    assert p.id in project_ids
    assert len(project_ids) == 1


@pytest.mark.django_db
def test_non_member_cannot_retrieve_project(authed_client, member_user):
    p = ProjectFactory()
    resp = authed_client(member_user).get(f"/api/v1/projects/{p.id}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_pm_can_add_and_remove_member(authed_client, pm_user, member_user):
    p = ProjectFactory()
    ProjectMembership.objects.filter(project=p, user=pm_user).update_or_create(
                project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    resp = authed_client(pm_user).post(
        f"/api/v1/projects/{p.id}/members/",
        {"user": member_user.id, "role": ProjectMembership.Role.MEMBER},
        format="json",
    )
    assert resp.status_code == 201, resp.data

    rm = authed_client(pm_user).delete(f"/api/v1/projects/{p.id}/members/{member_user.id}/")
    assert rm.status_code == 204
    assert not ProjectMembership.objects.filter(project=p, user=member_user).exists()


@pytest.mark.django_db
def test_member_cannot_add_member(authed_client, member_user):
    p = ProjectFactory()
    ProjectMembership.objects.create(project=p, user=member_user)
    other = User.objects.create_user(username="other", email="o@pms.local", password="pass12345")
    resp = authed_client(member_user).post(
        f"/api/v1/projects/{p.id}/members/",
        {"user": other.id, "role": ProjectMembership.Role.MEMBER},
        format="json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_computed_progress_is_average_of_tasks(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.filter(project=p, user=pm_user).update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    from apps.tasks.tests.factories import TaskFactory
    TaskFactory(project=p, progress=100)
    TaskFactory(project=p, progress=50)
    resp = authed_client(pm_user).get(f"/api/v1/projects/{p.id}/")
    assert resp.data["progress"] == 75.0


@pytest.mark.django_db
def test_activity_endpoint(authed_client, pm_user):
    resp = authed_client(pm_user).post("/api/v1/projects/", {
        "title": "Logged Project", "start_date": "2026-01-01",
    }, format="json")
    project_id = resp.data["id"]
    resp2 = authed_client(pm_user).get(f"/api/v1/projects/{project_id}/activity/")
    assert resp2.status_code == 200
    assert any(log["verb"] == "PROJECT_CREATED" for log in resp2.data)
