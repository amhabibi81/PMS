from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """List your notifications; mark read/unread."""

    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("task")
            .order_by("-created_at")
        )
        unread_only = self.request.query_params.get("unread") in ("true", "1")
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.save(update_fields=["is_read"])
        return Response(NotificationSerializer(n).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"marked_read": updated}, status=status.HTTP_200_OK)
