import datetime as dt

import pytest

from apps.projects.models import ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.tasks import services as task_services
from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory


def _setup(pm_user, **project_kwargs):
    p = ProjectFactory(**project_kwargs)
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    return p


@pytest.mark.django_db
def test_csv_export_status_distribution(authed_client, pm_user):
    p = _setup(pm_user)
    resp = authed_client(pm_user).get(
        f"/api/v1/reports/projects/{p.id}/export/?fmt=csv&type=status-distribution"
    )
    assert resp.status_code == 200
    assert "text/csv" in resp["Content-Type"]


@pytest.mark.django_db
def test_csv_export_workload_and_overdue(authed_client, pm_user, member_user):
    p = _setup(pm_user)
    ProjectMembership.objects.create(project=p, user=member_user)
    TaskFactory(project=p, assignee=member_user, status=Task.Status.TODO,
                due_date=dt.date.today() - dt.timedelta(days=2))
    for t in ("workload", "overdue"):
        resp = authed_client(pm_user).get(
            f"/api/v1/reports/projects/{p.id}/export/?fmt=csv&type={t}"
        )
        assert resp.status_code == 200


@pytest.mark.django_db
def test_export_invalid_format_returns_400(authed_client, pm_user):
    p = _setup(pm_user)
    resp = authed_client(pm_user).get(
        f"/api/v1/reports/projects/{p.id}/export/?fmt=xml"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_progress_over_time_endpoint(authed_client, pm_user):
    p = _setup(pm_user)
    t = TaskFactory(project=p, status=Task.Status.IN_PROGRESS, progress=0)
    task_services.set_progress(task=t, actor=pm_user, value=50)
    resp = authed_client(pm_user).get(
        f"/api/v1/reports/projects/{p.id}/progress-over-time/?days=30"
    )
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["project_progress"] == 50.0


@pytest.mark.django_db
def test_admin_can_access_any_project_report(authed_client, admin_user, pm_user):
    p = _setup(pm_user)
    resp = authed_client(admin_user).get(
        f"/api/v1/reports/projects/{p.id}/summary/"
    )
    assert resp.status_code == 200


@pytest.mark.django_db
def test_summary_at_risk_due_to_late_completion(pm_user):
    p = _setup(pm_user, due_date=dt.date.today() - dt.timedelta(days=5))
    TaskFactory(project=p, status=Task.Status.IN_PROGRESS, progress=10)
    from apps.reports import services

    s = services.project_summary(p)
    assert s["at_risk"] is True
