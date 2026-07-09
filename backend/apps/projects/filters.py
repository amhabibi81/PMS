import django_filters

from .models import Project, ProjectMembership


class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Project
        fields = ["status", "title"]
