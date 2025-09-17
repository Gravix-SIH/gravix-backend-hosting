from django.urls import path
from .views import (
    AssessmentListCreateView,
    CounselorListView,
    BookingListCreateView,
    BookingDetailView,
    ResourceListView,
)

urlpatterns = [
    path('assessments/', AssessmentListCreateView.as_view(), name='assessment-list-create'),
    path('counselors/', CounselorListView.as_view(), name='counselor-list'),
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('resources/', ResourceListView.as_view(), name='resource-list'),
]
