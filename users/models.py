import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        COUNSELOR = "counsellor", "Counselor"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    is_anonymous = models.BooleanField(default=False)
    anon_id = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def save(self, *args, **kwargs):
        if not self.anon_id:
            self.anon_id = f"anon_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
