from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from permissions import IsAdmin
from assessments.models import Assessment
from assessments.serializers import AssessmentSerializer
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from users.models import User


class IsCounselor:
    """Mixin to enforce counsellor role."""

    def check_role(self):
        if not hasattr(self, "request") or not self.request.user.is_authenticated:
            from rest_framework.exceptions import NotAuthenticated
            raise NotAuthenticated()
        if self.request.user.role != "counsellor":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only counselors can access this endpoint.")


class CounselorStatsView(APIView):
    """
    GET /api/counsellor/stats/ - Dashboard stats for counsellor
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "counsellor":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only counselors can access this endpoint.")

        user = request.user
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        # My upcoming bookings (confirmed/pending, date >= today)
        upcoming_bookings = Booking.objects.filter(
            counsellor=user, date__gte=today, status__in=["pending", "confirmed"]
        ).count()

        # Total completed sessions
        completed = Booking.objects.filter(
            counsellor=user, status="completed"
        ).count()

        # Students seen (unique students)
        students_seen = Booking.objects.filter(
            counsellor=user, status="completed"
        ).values("student").distinct().count()

        # Assessments to review (students assigned to this counsellor have submissions)
        student_ids = Booking.objects.filter(counsellor=user).values_list("student_id", flat=True).distinct()
        assessments_pending = Assessment.objects.filter(user_id__in=student_ids).count()

        # Recent submissions (last 30 days)
        recent_submissions = Assessment.objects.filter(
            user_id__in=student_ids,
            created_at__gte=timezone.now() - timedelta(days=30),
        ).count()

        return Response(
            {
                "upcoming_sessions": upcoming_bookings,
                "completed_sessions": completed,
                "students_seen": students_seen,
                "assessments_to_review": assessments_pending,
                "recent_submissions": recent_submissions,
            }
        )


class CounselorAssessmentListView(generics.ListAPIView):
    """
    GET /api/counsellor/assessments/ - List all student assessment submissions
   Counsellors see assessments from students they've had sessions with.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        if self.request.user.role != "counsellor":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only counselors can access this endpoint.")

        user = self.request.user
        # Get students this counsellor has had bookings with
        student_ids = Booking.objects.filter(
            counsellor=user
        ).values_list("student_id", flat=True).distinct()

        queryset = (
            Assessment.objects.filter(user_id__in=student_ids)
            .select_related("user")
            .order_by("-created_at")
        )

        # Filter by assessment type
        atype = self.request.query_params.get("assessment_type")
        if atype:
            queryset = queryset.filter(assessment_type=atype)

        # Filter by severity
        severity = self.request.query_params.get("severity")
        if severity:
            queryset = queryset.filter(severity__icontains=severity)

        return queryset


class CounselorBookingListView(generics.ListAPIView):
    """
    GET /api/counsellor/bookings/ - List all bookings for this counsellor
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        if self.request.user.role != "counsellor":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only counselors can access this endpoint.")

        user = self.request.user
        queryset = (
            Booking.objects.filter(counsellor=user)
            .select_related("student", "counsellor")
            .order_by("-date", "-created_at")
        )

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class CounselorBookingUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/counsellor/bookings/<uuid>/ - Update own booking status
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    lookup_field = "id"

    def get_queryset(self):
        if self.request.user.role != "counsellor":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only counselors can access this endpoint.")

        return Booking.objects.filter(counsellor=self.request.user)

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        old_status = booking.status

        serializer = self.get_serializer(
            booking, data=request.data, partial=True
        )
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
