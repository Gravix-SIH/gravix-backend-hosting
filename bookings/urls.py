from django.urls import path
from .views import BookingListCreateView, BookingDetailView, UpcomingBookingsView, CounselorListView, BookingConfirmView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list'),
    path('upcoming/', UpcomingBookingsView.as_view(), name='booking-upcoming'),
    path('counsellors/', CounselorListView.as_view(), name='counsellor-list'),
    path('<uuid:id>/confirm/', BookingConfirmView.as_view(), name='booking-confirm'),
    path('<uuid:id>', BookingDetailView.as_view(), name='booking-detail'),
]
