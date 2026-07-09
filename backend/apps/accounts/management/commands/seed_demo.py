"""Seed demo data for the thesis defense.

Run via: docker compose run --rm backend python manage.py seed_demo
Idempotent: safe to run repeatedly (creates missing records, skips existing).
"""
import datetime as dt

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMembership
from apps.tasks.models import Task


DEMO_USERS = [
    {"username": "admin", "email": "admin@pms.local", "password": "admin12345", "role": User.Role.ADMIN, "is_staff": True, "is_superuser": True, "first_name": "Ada", "last_name": "Admin"},
    {"username": "pm", "email": "pm@pms.local", "password": "pm12345", "role": User.Role.PROJECT_MANAGER, "first_name": "Parsa", "last_name": "Manager"},
    {"username": "member", "email": "member@pms.local", "password": "member12345", "role": User.Role.MEMBER, "first_name": "Mina", "last_name": "Member"},
]


class Command(BaseCommand):
    help = "Seed demo users, a sample project, and a few tasks for the thesis defense."

    @transaction.atomic
    def handle(self, *args, **options):
        created_users = {}
        for u in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=u["username"],
                defaults={
                    "email": u["email"],
                    "role": u["role"],
                    "is_staff": u.get("is_staff", False),
                    "is_superuser": u.get("is_superuser", False),
                    "first_name": u.get("first_name", ""),
                    "last_name": u.get("last_name", ""),
                },
            )
            if created:
                user.set_password(u["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {user.username} ({user.role})"))
            else:
                self.stdout.write(f"User {user.username} already exists, skipping.")
            created_users[u["username"]] = user

        pm = created_users["pm"]
        member = created_users["member"]
        admin = created_users["admin"]

        project, created = Project.objects.get_or_create(
            title="Thesis Demo Project",
            defaults={
                "description": "A sample project to demonstrate the PMS at the thesis defense.",
                "start_date": dt.date.today(),
                "due_date": dt.date.today() + dt.timedelta(days=30),
                "status": Project.Status.ACTIVE,
                "created_by": pm,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created project {project.title}"))
        else:
            self.stdout.write(f"Project {project.title} already exists, skipping.")

        for u, role in [(pm, ProjectMembership.Role.MANAGER), (member, ProjectMembership.Role.MEMBER), (admin, ProjectMembership.Role.MANAGER)]:
            ProjectMembership.objects.get_or_create(
                project=project, user=u, defaults={"role": role}
            )

        if not project.tasks.exists():
            Task.objects.create(
                project=project, title="Define requirements", reporter=pm, assignee=member,
                status=Task.Status.DONE, priority=Task.Priority.HIGH, progress=100,
                due_date=dt.date.today() + dt.timedelta(days=5),
            )
            Task.objects.create(
                project=project, title="Design database schema", reporter=pm, assignee=member,
                status=Task.Status.IN_PROGRESS, priority=Task.Priority.HIGH, progress=60,
                due_date=dt.date.today() + dt.timedelta(days=10),
            )
            Task.objects.create(
                project=project, title="Build Kanban board UI", reporter=pm, assignee=member,
                status=Task.Status.TODO, priority=Task.Priority.MEDIUM, progress=0,
                due_date=dt.date.today() + dt.timedelta(days=20),
            )
            Task.objects.create(
                project=project, title="Write thesis report", reporter=pm, assignee=None,
                status=Task.Status.TODO, priority=Task.Priority.LOW, progress=0,
                due_date=dt.date.today() + dt.timedelta(days=28),
            )
            self.stdout.write(self.style.SUCCESS("Created 4 demo tasks"))
        else:
            self.stdout.write("Tasks already exist, skipping.")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
