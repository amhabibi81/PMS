import csv
import datetime as dt

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMembership

from . import services


class Echo:
    """An object that just returns what it's given (for streaming CSV)."""

    def write(self, value):
        return value


class ProjectReportPermission(IsAuthenticated):
    """Authenticated + must be a member of the project (or Admin)."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        project_id = view.kwargs.get("project_id")
        project = get_object_or_404(Project, pk=project_id)
        if request.user.role == User.Role.ADMIN:
            return True
        return ProjectMembership.objects.filter(project=project, user=request.user).exists()


class StatusDistributionView(APIView):
    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        data = services.status_distribution(project)
        return Response(data)


class ProgressOverTimeView(APIView):
    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        days = int(request.query_params.get("days", 30))
        data = services.progress_over_time(project, days=days)
        return Response(data)


class WorkloadView(APIView):
    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        data = services.workload_per_member(project)
        return Response(data)


class OverdueView(APIView):
    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        data = services.overdue_tasks(project)
        return Response(data)


class SummaryView(APIView):
    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        return Response(services.project_summary(project))


class ExportView(APIView):
    """Export a report as CSV (StreamingHttpResponse) or PDF (WeasyPrint)."""

    permission_classes = (ProjectReportPermission,)

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        fmt = (request.query_params.get("fmt") or "csv").lower()
        report_type = (request.query_params.get("type") or "summary").lower()

        if fmt == "csv":
            rows = services.build_csv_rows(report_type, project)
            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer)
            filename = f"report_{report_type}_{project_id}_{timezone.now():%Y%m%d}.csv"
            response = StreamingHttpResponse(
                (writer.writerow(r) for r in rows),
                content_type="text/csv",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        if fmt == "pdf":
            try:
                from weasyprint import HTML
            except ImportError:
                return Response(
                    {"detail": "PDF export requires WeasyPrint, which is not installed."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            html = render_to_string("reports/project_report.html", services.build_report_context(project))
            pdf = HTML(string=html).write_pdf()
            filename = f"report_{project_id}_{timezone.now():%Y%m%d}.pdf"
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        return Response(
            {"detail": "format must be 'csv' or 'pdf'."}, status=status.HTTP_400_BAD_REQUEST
        )
