import datetime as dt

import pytest

from apps.projects.models import Project, ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.reports import services
from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory


@pytest.mark.django_db
def test_status_distribution(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    TaskFactory(project=p, status=Task.Status.TODO)
    TaskFactory(project=p, status=Task.Status.DONE)
    resp = authed_client(pm_user).get(f"/api/v1/reports/projects/{p.id}/status-distribution/")
    assert resp.status_code == 200
    by_status = {r["status"]: r["count"] for r in resp.data}
    assert by_status.get("Todo") == 1
    assert by_status.get("Done") == 1


@pytest.mark.django_db
def test_summary_on_track(authed_client, pm_user):
    p = ProjectFactory(due_date=dt.date.today() + dt.timedelta(days=30))
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    TaskFactory(project=p, status=Task.Status.DONE, progress=100)
    s = services.project_summary(p)
    assert s["at_risk"] is False
    assert s["flag"] == "OnTrack"


@pytest.mark.django_db
def test_summary_at_risk_when_overdue_ratio_high(pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    TaskFactory(project=p, status=Task.Status.TODO, due_date=dt.date.today() - dt.timedelta(days=5))
    TaskFactory(project=p, status=Task.Status.TODO, due_date=dt.date.today() - dt.timedelta(days=5))
    TaskFactory(project=p, status=Task.Status.DONE, progress=100)
    TaskFactory(project=p, status=Task.Status.DONE, progress=100)
    s = services.project_summary(p)
    assert s["at_risk"] is True


@pytest.mark.django_db
def test_overdue_includes_days_late(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    TaskFactory(project=p, status=Task.Status.TODO, due_date=dt.date.today() - dt.timedelta(days=3))
    resp = authed_client(pm_user).get(f"/api/v1/reports/projects/{p.id}/overdue/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["days_late"] == 3


@pytest.mark.django_db
def test_workload_counts(authed_client, pm_user, member_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    ProjectMembership.objects.create(project=p, user=member_user)
    TaskFactory(project=p, assignee=member_user, status=Task.Status.TODO)
    TaskFactory(project=p, assignee=member_user, status=Task.Status.IN_PROGRESS)
    TaskFactory(project=p, assignee=member_user, status=Task.Status.DONE)
    resp = authed_client(pm_user).get(f"/api/v1/reports/projects/{p.id}/workload/")
    assert resp.status_code == 200
    target = [r for r in resp.data if r["user_id"] == member_user.id][0]
    assert target["open_tasks"] == 2


@pytest.mark.django_db
def test_csv_export(authed_client, pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    resp = authed_client(pm_user).get(
        f"/api/v1/reports/projects/{p.id}/export/?fmt=csv&type=summary"
    )
    assert resp.status_code == 200
    assert resp["Content-Type"] == "text/csv"
    assert "attachment" in resp["Content-Disposition"]


@pytest.mark.django_db
def test_non_member_blocked_from_reports(authed_client, member_user):
    p = ProjectFactory()
    resp = authed_client(member_user).get(f"/api/v1/reports/projects/{p.id}/summary/")
    assert resp.status_code == 403
