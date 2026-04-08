from django.db import models
from users.models import User
import uuid


class Booking(models.Model):
    class SessionType(models.TextChoices):
        VIDEO = "video", "Video Call"
        IN_PERSON = "in-person", "In-Person"
        PHONE = "phone", "Phone Call"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_bookings')
    counsellor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='counsellor_bookings')
    date = models.DateField()
    time = models.CharField(max_length=20)
    session_type = models.CharField(max_length=20, choices=SessionType.choices, default=SessionType.VIDEO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True, default="")
    # Meeting details - filled by counsellor when confirming
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    meeting_phone = models.CharField(max_length=20, blank=True, null=True)
    meeting_address = models.TextField(max_length=500, blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student.name} -> {self.counsellor.name} on {self.date}"

    def get_meeting_details(self):
        """Return meeting details based on session type."""
        if self.session_type == self.SessionType.VIDEO:
            return self.meeting_link
        elif self.session_type == self.SessionType.PHONE:
            return self.meeting_phone
        elif self.session_type == self.SessionType.IN_PERSON:
            return self.meeting_address
        return None
