from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")

app_name = "projects"

urlpatterns = [
    path("", include(router.urls)),
]
