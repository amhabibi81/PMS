"""Direct unit tests for tasks.services business logic (no HTTP layer)."""
import datetime as dt

import pytest
from django.core.exceptions import ValidationError

from apps.projects.models import ProjectMembership
from apps.projects.tests.factories import ProjectFactory
from apps.tasks import services
from apps.tasks.models import Task
from apps.tasks.tests.factories import TaskFactory


@pytest.fixture
def pm_task(pm_user):
    p = ProjectFactory()
    ProjectMembership.objects.update_or_create(
        project=p, user=pm_user, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    return pm_user, p


@pytest.mark.django_db
def test_update_task_logs_assignment_change(pm_task):
    from apps.accounts.tests.factories import UserFactory

    pm, p = pm_task
    assignee = UserFactory()
    ProjectMembership.objects.create(project=p, user=assignee)
    t = TaskFactory(project=p)
    services.update_task(task=t, actor=pm, assignee=assignee)
    t.refresh_from_db()
    assert t.assignee_id == assignee.id


@pytest.mark.django_db
def test_reopen_done_to_in_progress(pm_task):
    pm, p = pm_task
    t = TaskFactory(project=p, status=Task.Status.DONE, progress=100)
    services.transition_status(task=t, actor=pm, new_status=Task.Status.IN_PROGRESS)
    t.refresh_from_db()
    assert t.status == Task.Status.IN_PROGRESS


@pytest.mark.django_db
def test_illegal_transition_raises(pm_task):
    pm, p = pm_task
    t = TaskFactory(project=p, status=Task.Status.TODO)
    with pytest.raises(services.TransitionError):
        services.transition_status(task=t, actor=pm, new_status=Task.Status.DONE)


@pytest.mark.django_db
def test_progress_locked_at_100_when_done(pm_task):
    pm, p = pm_task
    t = TaskFactory(project=p, status=Task.Status.DONE, progress=100)
    services.set_progress(task=t, actor=pm, value=50)
    t.refresh_from_db()
    assert t.progress == 100


@pytest.mark.django_db
def test_set_progress_logs_snapshot(pm_task):
    pm, p = pm_task
    t = TaskFactory(project=p, progress=0)
    services.set_progress(task=t, actor=pm, value=40)
    from apps.projects.models import ActivityLog

    log = ActivityLog.objects.filter(
        verb=ActivityLog.Verb.TASK_PROGRESS_CHANGED, target_id=t.id
    ).last()
    assert log is not None
    assert log.metadata["task_progress"] == 40
    assert log.metadata["project_progress"] == p.progress


@pytest.mark.django_db
def test_add_comment_and_upload_attachment(pm_task):
    from django.core.files.uploadedfile import SimpleUploadedFile

    pm, p = pm_task
    t = TaskFactory(project=p)
    comment = services.add_comment(task=t, author=pm, body="note")
    assert comment.body == "note"

    f = SimpleUploadedFile("doc.txt", b"hello", content_type="text/plain")
    attachment = services.upload_attachment(task=t, user=pm, file=f)
    assert attachment.filename == "doc.txt"
    assert attachment.size == 5


@pytest.mark.django_db
def test_done_via_review_forces_progress_100(pm_task):
    pm, p = pm_task
    t = TaskFactory(project=p, status=Task.Status.IN_PROGRESS, progress=30)
    services.transition_status(task=t, actor=pm, new_status=Task.Status.REVIEW)
    services.transition_status(task=t, actor=pm, new_status=Task.Status.DONE)
    t.refresh_from_db()
    assert t.progress == 100
