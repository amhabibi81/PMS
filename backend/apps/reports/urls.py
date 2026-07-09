from django.urls import path

from .views import (
    ExportView,
    OverdueView,
    ProgressOverTimeView,
    StatusDistributionView,
    SummaryView,
    WorkloadView,
)

app_name = "reports"

urlpatterns = [
    path("reports/projects/<int:project_id>/status-distribution/", StatusDistributionView.as_view(), name="status-distribution"),
    path("reports/projects/<int:project_id>/progress-over-time/", ProgressOverTimeView.as_view(), name="progress-over-time"),
    path("reports/projects/<int:project_id>/workload/", WorkloadView.as_view(), name="workload"),
    path("reports/projects/<int:project_id>/overdue/", OverdueView.as_view(), name="overdue"),
    path("reports/projects/<int:project_id>/summary/", SummaryView.as_view(), name="summary"),
    path("reports/projects/<int:project_id>/export/", ExportView.as_view(), name="export"),
]
