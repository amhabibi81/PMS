import factory

from apps.accounts.tests.factories import UserFactory
from apps.projects.tests.factories import ProjectFactory
from apps.tasks.models import Task, TaskComment


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    project = factory.SubFactory(ProjectFactory)
    title = factory.Sequence(lambda n: f"Task {n}")
    description = "A test task."
    status = Task.Status.TODO
    priority = Task.Priority.MEDIUM
    progress = 0
    reporter = factory.SubFactory(UserFactory)

    @factory.post_generation
    def assignee_membership(obj, create, extracted, **kwargs):
        if not create:
            return
        if obj.assignee and not obj.project.memberships.filter(user=obj.assignee).exists():
            from apps.projects.models import ProjectMembership
            ProjectMembership.objects.create(project=obj.project, user=obj.assignee)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaskComment

    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(UserFactory)
    body = "A test comment."
