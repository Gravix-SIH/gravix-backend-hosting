from django.db import models
from django.conf import settings

class Assessment(models.Model):
    TYPE_CHOICES = [
        ('phq9', 'PHQ-9'),
        ('gad7', 'GAD-7'),
        ('combined', 'Combined'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    anon_id = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    responses = models.JSONField()
    score = models.PositiveIntegerField()
    risk_level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.user.username if self.user else self.anon_id or "Anonymous"
        return f"{who} - {self.type} ({self.risk_level})"


class Counselor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    available_slots = models.JSONField(default=list)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    anon_id = models.CharField(max_length=50, null=True, blank=True)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE)
    assessment = models.ForeignKey(
        Assessment, null=True, blank=True, on_delete=models.SET_NULL
    )
    scheduled_time = models.DateTimeField()
    privacy_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Booking with {self.counselor.name} on {self.scheduled_time}"


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('wellness', 'Wellness'),
        ('selfhelp', 'Self-Help'),
        ('crisis', 'Crisis'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()  # could hold HTML or Markdown
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"
