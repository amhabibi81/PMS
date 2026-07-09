from .models import ActivityLog, Project, ProjectMembership


def log_activity(actor, verb, project, target_type, target_id, metadata=None):
    """Append-only activity log. Safe to call inside a transaction."""
    return ActivityLog.objects.create(
        actor=actor,
        verb=verb,
        project=project,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata or {},
    )


def create_project(*, actor, **fields):
    """Admin/PM creates a project; creator becomes Manager member."""
    project = Project.objects.create(created_by=actor, **fields)
    ProjectMembership.objects.get_or_create(
        project=project, user=actor, defaults={"role": ProjectMembership.Role.MANAGER}
    )
    log_activity(
        actor, ActivityLog.Verb.PROJECT_CREATED, project,
        target_type="Project", target_id=project.id,
        metadata={"title": project.title, "status": project.status},
    )
    return project


def update_project(*, project, actor, **fields):
    for k, v in fields.items():
        setattr(project, k, v)
    project.save()
    log_activity(
        actor, ActivityLog.Verb.PROJECT_UPDATED, project,
        target_type="Project", target_id=project.id,
        metadata={k: str(v) for k, v in fields.items()},
    )
    return project


def add_member(*, project, actor, user, role=ProjectMembership.Role.MEMBER):
    membership, created = ProjectMembership.objects.get_or_create(
        project=project, user=user, defaults={"role": role}
    )
    if created:
        log_activity(
            actor, ActivityLog.Verb.MEMBER_ADDED, project,
            target_type="User", target_id=user.id,
            metadata={"username": user.username, "role": role},
        )
    return membership


def remove_member(*, project, actor, user):
    deleted, _ = ProjectMembership.objects.filter(project=project, user=user).delete()
    if deleted:
        log_activity(
            actor, ActivityLog.Verb.MEMBER_REMOVED, project,
            target_type="User", target_id=user.id,
            metadata={"username": user.username},
        )
    return deleted
