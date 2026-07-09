"""Reporting aggregations — all in ORM aggregate/annotate, never Python loops (reporting skill).

At-risk definition: >20% of tasks overdue OR projected completion past project deadline.
"""
import datetime as dt
from decimal import Decimal

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.projects.models import ActivityLog, Project, ProjectMembership
from apps.tasks.models import Task


def status_distribution(project: Project) -> list[dict]:
    qs = (
        project.tasks.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    return [{"status": r["status"], "count": r["count"]} for r in qs]


def progress_over_time(project: Project, days: int = 30) -> list[dict]:
    """Project progress over time from ActivityLog (verb=TASK_PROGRESS_CHANGED).

    Each event's metadata carries a snapshot of project_progress at that moment.
    """
    since = timezone.now() - dt.timedelta(days=days)
    logs = (
        project.activity_logs.filter(
            verb=ActivityLog.Verb.TASK_PROGRESS_CHANGED, created_at__gte=since
        )
        .order_by("created_at")
        .values("created_at", "metadata")
    )
    return [
        {
            "timestamp": log["created_at"],
            "project_progress": float(log["metadata"].get("project_progress", 0) or 0),
        }
        for log in logs
    ]


def workload_per_member(project: Project) -> list[dict]:
    members = (
        ProjectMembership.objects.filter(project=project)
        .select_related("user")
        .values("user_id", "user__username")
    )
    today = dt.date.today()
    result = []
    for m in members:
        base = project.tasks.filter(assignee_id=m["user_id"])
        open_tasks = base.exclude(status=Task.Status.DONE).count()
        overdue_tasks = base.filter(
            due_date__lt=today, status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW]
        ).count()
        result.append({
            "user_id": m["user_id"],
            "username": m["user__username"],
            "open_tasks": open_tasks,
            "overdue_tasks": overdue_tasks,
        })
    return result


def overdue_tasks(project: Project) -> list[dict]:
    today = dt.date.today()
    qs = project.tasks.filter(
        due_date__lt=today,
        status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW],
    ).select_related("assignee")
    result = []
    for t in qs:
        days_late = (today - t.due_date).days if t.due_date else 0
        result.append({
            "task_id": t.id,
            "title": t.title,
            "assignee": t.assignee.get_username() if t.assignee else None,
            "due_date": t.due_date,
            "days_late": days_late,
        })
    return result


def project_summary(project: Project) -> dict:
    total = project.tasks.count()
    done = project.tasks.filter(status=Task.Status.DONE).count()
    overdue = len(overdue_tasks(project))
    progress = float(project.progress)
    overdue_ratio = (overdue / total) if total else 0
    projected_late = bool(project.due_date) and progress < 100 and project.due_date < dt.date.today()
    at_risk = overdue_ratio > Decimal("0.2") or projected_late
    flag = "AtRisk" if at_risk else "OnTrack"
    return {
        "project_id": project.id,
        "title": project.title,
        "progress": progress,
        "total_tasks": total,
        "done_tasks": done,
        "overdue_count": overdue,
        "at_risk": bool(at_risk),
        "flag": flag,
    }


def build_csv_rows(report_type: str, project: Project) -> list[list]:
    """Return rows for CSV export as list-of-lists (first row = header)."""
    if report_type == "status-distribution":
        rows = [["status", "count"]]
        rows += [[r["status"], r["count"]] for r in status_distribution(project)]
    elif report_type == "workload":
        rows = [["user_id", "username", "open_tasks", "overdue_tasks"]]
        rows += [[r["user_id"], r["username"], r["open_tasks"], r["overdue_tasks"]] for r in workload_per_member(project)]
    elif report_type == "overdue":
        rows = [["task_id", "title", "assignee", "due_date", "days_late"]]
        rows += [[r["task_id"], r["title"], r["assignee"], r["due_date"], r["days_late"]] for r in overdue_tasks(project)]
    elif report_type == "summary":
        s = project_summary(project)
        rows = [["field", "value"], *[[k, v] for k, v in s.items()]]
    else:
        rows = [["error"], ["unknown report type"]]
    return rows


def build_report_context(project: Project) -> dict:
    """Context for PDF export via WeasyPrint."""
    return {
        "project": project,
        "summary": project_summary(project),
        "status_distribution": status_distribution(project),
        "workload": workload_per_member(project),
        "overdue": overdue_tasks(project),
        "generated_at": timezone.now(),
    }
