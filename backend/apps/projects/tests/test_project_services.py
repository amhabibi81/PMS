import pytest

from apps.accounts.tests.factories import UserFactory
from apps.projects import services
from apps.projects.models import ActivityLog
from apps.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
def test_update_project_logs_activity(pm_user):
    # Factory auto-creates the PM membership for created_by.
    p = ProjectFactory(created_by=pm_user)
    services.update_project(project=p, actor=pm_user, title="Updated")
    p.refresh_from_db()
    assert p.title == "Updated"
    assert ActivityLog.objects.filter(
        verb=ActivityLog.Verb.PROJECT_UPDATED, target_id=p.id
    ).exists()


@pytest.mark.django_db
def test_add_member_idempotent(pm_user):
    p = ProjectFactory(created_by=pm_user)
    other = UserFactory()
    m1 = services.add_member(project=p, actor=pm_user, user=other, role="Member")
    m2 = services.add_member(project=p, actor=pm_user, user=other, role="Member")
    assert m1.id == m2.id


@pytest.mark.django_db
def test_remove_member_returns_count_and_logs(pm_user):
    p = ProjectFactory(created_by=pm_user)
    other = UserFactory()
    services.add_member(project=p, actor=pm_user, user=other)
    deleted = services.remove_member(project=p, actor=pm_user, user=other)
    assert deleted == 1
    assert ActivityLog.objects.filter(
        verb=ActivityLog.Verb.MEMBER_REMOVED, target_id=other.id
    ).exists()


@pytest.mark.django_db
def test_remove_nonexistent_member_returns_zero(pm_user):
    p = ProjectFactory(created_by=pm_user)
    other = UserFactory()
    assert services.remove_member(project=p, actor=pm_user, user=other) == 0
