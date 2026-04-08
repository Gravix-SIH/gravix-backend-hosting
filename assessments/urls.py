from django.urls import path
from .views import AssessmentListCreateView, AssessmentDetailView, WeeklyHealthScoreView

urlpatterns = [
    path('', AssessmentListCreateView.as_view(), name='assessment-list'),
    path('health/score/', WeeklyHealthScoreView.as_view(), name='health-score'),
    path('<uuid:pk>', AssessmentDetailView.as_view(), name='assessment-detail'),
]
