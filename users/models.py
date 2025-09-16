import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        COUNSELOR = "counselor", "Counselor"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    anon_id = models.CharField(max_length=50, null=True, blank=True)
    college = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=5, choices=[('en','English'),('hi','Hindi'),('ta','Tamil')], default='en')
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def generate_anon_id(self):
        self.anon_id = f"anon_{uuid.uuid4().hex[:8]}"
        self.save(update_fields=["anon_id"])
        return self.anon_id

    def save(self, *args, **kwargs):
        if not self.anon_id:
            self.anon_id = f"anon_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)