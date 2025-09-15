"""
Models for MindMate Chatbot
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatSession(models.Model):
    """Chat session for tracking user conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, db_index=True)  # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.id} - {self.user_id}"


class Conversation(models.Model):
    """Individual conversation exchanges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='conversations')
    user_message = models.TextField()
    bot_response = models.TextField()
    mood_detected = models.CharField(max_length=50, blank=True, null=True)
    crisis_detected = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Conversation {self.id} - {self.session.user_id}"


class MoodEntry(models.Model):
    """Mood tracking entries"""
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('angry', 'Angry'),
        ('confused', 'Confused'),
        ('lonely', 'Lonely'),
        ('scared', 'Scared'),
        ('depressed', 'Depressed'),
        ('stressed', 'Stressed'),
        ('calm', 'Calm'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='mood_entries')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    context = models.CharField(max_length=255, blank=True)  # Brief context
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.mood} - {self.session.user_id} - {self.timestamp.date()}"


class Assessment(models.Model):
    """Mental health assessment results"""
    ASSESSMENT_TYPES = [
        ('phq9', 'PHQ-9 Depression Screening'),
        ('gad7', 'GAD-7 Anxiety Screening'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=10, choices=ASSESSMENT_TYPES)
    total_score = models.IntegerField()
    responses = models.JSONField()  # Store individual question responses
    interpretation = models.TextField(blank=True)  # AI-generated interpretation
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.assessment_type.upper()} - {self.total_score} - {self.session.user_id}"


class UserProfile(models.Model):
    """User profile for tracking engagement"""
    user_id = models.CharField(max_length=255, unique=True, primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    total_conversations = models.IntegerField(default=0)
    total_assessments = models.IntegerField(default=0)
    preferences = models.JSONField(default=dict, blank=True)  # User preferences

    def __str__(self):
        return f"Profile - {self.user_id}"