"""
Serializers for MindMate Chatbot API - External Backend
"""
from rest_framework import serializers
from .models import ChatSession, Conversation, MoodEntry, Assessment, UserProfile


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversation exchanges"""
    class Meta:
        model = Conversation
        fields = ['id', 'user_message', 'bot_response', 'mood_detected', 'crisis_detected', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for incoming chat requests"""
    message = serializers.CharField(max_length=2000)
    user_id = serializers.CharField(max_length=255, required=False)
    session_id = serializers.UUIDField(required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    response = serializers.CharField()
    session_id = serializers.UUIDField()
    mood_detected = serializers.CharField(required=False, allow_null=True)
    crisis_detected = serializers.BooleanField(default=False)
    suggestions = serializers.DictField(required=False)


class MoodEntrySerializer(serializers.ModelSerializer):
    """Serializer for mood entries"""
    class Meta:
        model = MoodEntry
        fields = ['id', 'mood', 'context', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for assessment results"""
    class Meta:
        model = Assessment
        fields = ['id', 'assessment_type', 'total_score', 'responses', 'interpretation', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'interpretation']


class AssessmentRequestSerializer(serializers.Serializer):
    """Serializer for assessment submission"""
    assessment_type = serializers.ChoiceField(choices=['phq9', 'gad7'])
    responses = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=3),
        min_length=7,
        max_length=9
    )
    user_id = serializers.CharField(max_length=255, required=False)
    session_id = serializers.UUIDField(required=False)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    class Meta:
        model = UserProfile
        fields = ['user_id', 'first_seen', 'last_activity', 'total_conversations', 'total_assessments', 'preferences']
        read_only_fields = ['first_seen', 'last_activity', 'total_conversations', 'total_assessments']


class SessionSummarySerializer(serializers.ModelSerializer):
    """Serializer for session summary"""
    recent_conversations = ConversationSerializer(many=True, read_only=True, source='conversations')
    recent_moods = MoodEntrySerializer(many=True, read_only=True, source='mood_entries')

    class Meta:
        model = ChatSession
        fields = ['id', 'user_id', 'created_at', 'updated_at', 'recent_conversations', 'recent_moods']