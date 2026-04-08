from django.urls import path
from .views import (
    AdminStatsView,
    AdminUserListView,
    AdminUserDetailView,
    AdminBookingListView,
    AdminBookingDetailView,
    AdminResourceListCreateView,
    AdminResourceDetailView,
    AdminAssessmentListView,
    AdminAssessmentStatsView,
)

urlpatterns = [
    path("stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<uuid:id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("bookings/", AdminBookingListView.as_view(), name="admin-booking-list"),
    path("bookings/<uuid:id>/", AdminBookingDetailView.as_view(), name="admin-booking-detail"),
    path("resources/", AdminResourceListCreateView.as_view(), name="admin-resource-list"),
    path("resources/<uuid:id>/", AdminResourceDetailView.as_view(), name="admin-resource-detail"),
    path("assessments/", AdminAssessmentListView.as_view(), name="admin-assessment-list"),
    path("assessments/stats/", AdminAssessmentStatsView.as_view(), name="admin-assessment-stats"),
]
