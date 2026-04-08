from django.db import models
from users.models import User
import uuid


class Assessment(models.Model):
    class AssessmentType(models.TextChoices):
        PHQ9 = "phq9", "PHQ-9 Depression Scale"
        GAD7 = "gad7", "GAD-7 Anxiety Scale"
        PSQI = "psqi", "Pittsburgh Sleep Quality Index"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    score = models.IntegerField()
    max_score = models.IntegerField()
    severity = models.CharField(max_length=50)
    answers = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.assessment_type}: {self.score}/{self.max_score}"


class WeeklyHealthScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_scores')
    score = models.IntegerField()
    change = models.IntegerField(default=0)
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_start']
        unique_together = ['user', 'week_start']

    def __str__(self):
        return f"{self.user.email} - Week of {self.week_start}: {self.score}"
