import datetime as dt

import factory

from apps.accounts.tests.factories import UserFactory
from apps.projects.models import Project, ProjectMembership


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Project {n}")
    description = "A test project."
    status = Project.Status.ACTIVE
    start_date = factory.LazyFunction(dt.date.today)
    due_date = factory.LazyFunction(lambda: dt.date.today() + dt.timedelta(days=30))
    created_by = factory.SubFactory(UserFactory, role="ProjectManager")

    @factory.post_generation
    def with_manager(obj, create, extracted, **kwargs):
        if not create or extracted is False:
            return
        ProjectMembership.objects.get_or_create(
            project=obj, user=obj.created_by,
            defaults={"role": ProjectMembership.Role.MANAGER},
        )


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectMembership

    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
    role = ProjectMembership.Role.MEMBER
