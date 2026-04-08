from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from permissions import IsAdmin
from users.models import User
from bookings.models import Booking
from assessments.models import Assessment
from resources.models import Resource
from .serializers import (
    AdminUserSerializer,
    AdminBookingSerializer,
    AdminResourceSerializer,
    AdminAssessmentSerializer,
)


# ─── Stats ───────────────────────────────────────────────────────────────────


class AdminStatsView(APIView):
    """
    GET /api/admin/stats/ - Dashboard overview stats
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        total_users = User.objects.count()
        total_students = User.objects.filter(role="student").count()
        total_counsellors = User.objects.filter(role="counsellor").count()
        total_admins = User.objects.filter(role="admin").count()

        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status="pending").count()
        confirmed_bookings = Booking.objects.filter(status="confirmed").count()
        bookings_this_week = Booking.objects.filter(date__gte=week_start).count()

        total_resources = Resource.objects.count()
        total_assessments = Assessment.objects.count()

        recent_bookings = Booking.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        recent_assessments = Assessment.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        return Response(
            {
                "users": {
                    "total": total_users,
                    "students": total_students,
                    "counsellors": total_counsellors,
                    "admins": total_admins,
                },
                "bookings": {
                    "total": total_bookings,
                    "pending": pending_bookings,
                    "confirmed": confirmed_bookings,
                    "this_week": bookings_this_week,
                },
                "resources": total_resources,
                "assessments": {
                    "total": total_assessments,
                    "this_week": recent_assessments,
                },
                "recent_activity": {
                    "bookings": recent_bookings,
                    "assessments": recent_assessments,
                },
            }
        )


# ─── Users ───────────────────────────────────────────────────────────────────


class AdminUserListView(generics.ListAPIView):
    """
    GET /api/admin/users/ - List all users (admin only)
    Supports: role, is_active, search query params
    """

    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by("-created_at")
        role = self.request.query_params.get("role")
        is_active = self.request.query_params.get("is_active")
        search = self.request.query_params.get("search")

        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/admin/users/<uuid:id>/ (admin only)
    """

    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def get_queryset(self):
        return User.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        old_role = user.role
        old_is_active = user.is_active

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        from auditlog.utils import log_admin_action

        details = {}
        if "role" in request.data and old_role != user.role:
            details["role_changed"] = {"from": old_role, "to": user.role}
        if "is_active" in request.data and old_is_active != user.is_active:
            details["is_active_changed"] = {
                "from": old_is_active,
                "to": user.is_active,
            }

        log_admin_action(request, "update", "User", user.id, details)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user_id = user.id
        user_email = user.email
        user.delete()

        from auditlog.utils import log_admin_action

        log_admin_action(
            request, "delete", "User", user_id, {"deleted_email": user_email}
        )
        return Response({"detail": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


# ─── Bookings ────────────────────────────────────────────────────────────────


class AdminBookingListView(generics.ListAPIView):
    """
    GET /api/admin/bookings/ - List all bookings with optional filters
    Supports: status, counsellor_id, student_id
    """

    serializer_class = AdminBookingSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = (
            Booking.objects.all()
            .select_related("student", "counsellor")
            .order_by("-date", "-created_at")
        )
        status_filter = self.request.query_params.get("status")
        counsellor_id = self.request.query_params.get("counsellor_id")
        student_id = self.request.query_params.get("student_id")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if counsellor_id:
            queryset = queryset.filter(counsellor_id=counsellor_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset


class AdminBookingDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/admin/bookings/<uuid:id>/ - Update booking status
    """

    serializer_class = AdminBookingSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def get_queryset(self):
        return Booking.objects.all()

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        old_status = booking.status

        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        from auditlog.utils import log_admin_action

        log_admin_action(
            request,
            "update",
            "Booking",
            booking.id,
            {"status_changed": {"from": old_status, "to": booking.status}},
        )
        return Response(serializer.data)


# ─── Resources ───────────────────────────────────────────────────────────────


class AdminResourceListCreateView(generics.ListCreateAPIView):
    """
    GET /api/admin/resources/ - List all | POST - Create new
    Supports: category filter
    """

    serializer_class = AdminResourceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Resource.objects.all().order_by("-created_at")
        category = self.request.query_params.get("category")
        if category and category != "all":
            queryset = queryset.filter(category__iexact=category)
        return queryset

    def perform_create(self, serializer):
        resource = serializer.save(created_by=self.request.user)

        from auditlog.utils import log_admin_action

        log_admin_action(
            request=self.request,
            action="create",
            target_type="Resource",
            target_id=resource.id,
            details={"title": resource.title, "type": resource.type},
        )


class AdminResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/admin/resources/<uuid:id>/
    """

    serializer_class = AdminResourceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def get_queryset(self):
        return Resource.objects.all()

    def patch(self, request, *args, **kwargs):
        resource = self.get_object()
        serializer = self.get_serializer(resource, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        from auditlog.utils import log_admin_action

        log_admin_action(request, "update", "Resource", resource.id, request.data)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        resource = self.get_object()
        resource_id = resource.id
        resource_title = resource.title
        resource.delete()

        from auditlog.utils import log_admin_action

        log_admin_action(
            request, "delete", "Resource", resource_id, {"title": resource_title}
        )
        return Response({"detail": "Resource deleted"}, status=status.HTTP_204_NO_CONTENT)


# ─── Assessments ─────────────────────────────────────────────────────────────


class AdminAssessmentStatsView(APIView):
    """
    GET /api/admin/assessments/stats/ - Aggregate assessment statistics
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        total_submissions = Assessment.objects.count()

        by_type = (
            Assessment.objects.values("assessment_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_submissions = Assessment.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        avg_scores = {}
        for atype in ["phq9", "gad7", "psqi"]:
            assessments = Assessment.objects.filter(assessment_type=atype)
            if assessments.exists():
                avg = sum(a.score for a in assessments) / assessments.count()
                avg_scores[atype] = round(avg, 1)

        return Response(
            {
                "total_submissions": total_submissions,
                "by_type": list(by_type),
                "recent_submissions": recent_submissions,
                "average_scores": avg_scores,
            }
        )


class AdminAssessmentListView(generics.ListAPIView):
    """
    GET /api/admin/assessments/ - List all assessment submissions
    Supports: assessment_type filter
    """

    serializer_class = AdminAssessmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Assessment.objects.select_related("user").all().order_by("-created_at")
        atype = self.request.query_params.get("assessment_type")
        if atype:
            queryset = queryset.filter(assessment_type=atype)
        return queryset
