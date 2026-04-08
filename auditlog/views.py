from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/admin/audit-logs/ - List audit logs (admin only)
    Supports filtering by: actor_id, target_type, action, date range
    """

    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by("-timestamp")
        actor_id = self.request.query_params.get("actor_id")
        target_type = self.request.query_params.get("target_type")
        action = self.request.query_params.get("action")

        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if action:
            queryset = queryset.filter(action=action)

        return queryset
