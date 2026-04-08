from django.urls import path
from .views import (
    CounselorStatsView,
    CounselorAssessmentListView,
    CounselorBookingListView,
    CounselorBookingUpdateView,
)

urlpatterns = [
    path("stats/", CounselorStatsView.as_view(), name="counsellor-stats"),
    path("assessments/", CounselorAssessmentListView.as_view(), name="counsellor-assessment-list"),
    path("bookings/", CounselorBookingListView.as_view(), name="counsellor-booking-list"),
    path("bookings/<uuid:id>/", CounselorBookingUpdateView.as_view(), name="counsellor-booking-update"),
]
