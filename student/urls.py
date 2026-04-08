from django.urls import path
from bookings.views import BookingListCreateView, BookingDetailView, UpcomingBookingsView, CounselorListView, CounselorSlotsView
from resources.views import ResourceListView, ResourceBookmarkListView, BookmarkResourceView
from assessments.views import AssessmentListCreateView, AssessmentDetailView, WeeklyHealthScoreView

urlpatterns = [
    path('bookings/', BookingListCreateView.as_view(), name='student-booking-list'),
    path('bookings/upcoming/', UpcomingBookingsView.as_view(), name='student-booking-upcoming'),
    path('bookings/counsellors/', CounselorListView.as_view(), name='student-counsellors'),
    path('bookings/slots/', CounselorSlotsView.as_view(), name='student-booking-slots'),
    path('bookings/<uuid:id>/', BookingDetailView.as_view(), name='student-booking-detail'),
    path('resources/', ResourceListView.as_view(), name='student-resource-list'),
    path('resources/bookmarks/', ResourceBookmarkListView.as_view(), name='student-bookmarks'),
    path('resources/<uuid:resource_id>/bookmark/', BookmarkResourceView.as_view(), name='student-bookmark'),
    path('health/score/', WeeklyHealthScoreView.as_view(), name='student-health-score'),
    path('assessments/', AssessmentListCreateView.as_view(), name='student-assessment-list'),
    path('assessments/<uuid:pk>/', AssessmentDetailView.as_view(), name='student-assessment-detail'),
]
