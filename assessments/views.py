from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from .models import Assessment, WeeklyHealthScore
from .serializers import AssessmentSerializer, AssessmentCreateSerializer, WeeklyHealthScoreSerializer


class AssessmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssessmentCreateSerializer
        return AssessmentSerializer

    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
        self._update_weekly_score()

    def _update_weekly_score(self):
        user = self.request.user
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        recent_assessments = Assessment.objects.filter(
            user=user,
            created_at__date__gte=week_start
        )

        if recent_assessments.exists():
            scores = []
            for a in recent_assessments:
                percentage = (a.score / a.max_score) * 100
                normalized = 100 - percentage
                scores.append(normalized)

            avg_score = sum(scores) / len(scores)
            score = int(avg_score)

            prev_week_start = week_start - timedelta(days=7)
            try:
                prev_score = WeeklyHealthScore.objects.get(user=user, week_start=prev_week_start)
                change = score - prev_score.score
            except WeeklyHealthScore.DoesNotExist:
                change = 0

            WeeklyHealthScore.objects.update_or_create(
                user=user,
                week_start=week_start,
                defaults={'score': score, 'change': change}
            )


class AssessmentDetailView(generics.RetrieveAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)


class WeeklyHealthScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        try:
            weekly = WeeklyHealthScore.objects.get(user=request.user, week_start=week_start)
            return Response({
                'score': weekly.score,
                'change': weekly.change
            })
        except WeeklyHealthScore.DoesNotExist:
            return Response({
                'score': None,
                'change': 0
            })
