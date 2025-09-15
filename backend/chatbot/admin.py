"""
Admin configuration for chatbot app
"""
from django.contrib import admin
from .models import ChatSession, Conversation, MoodEntry, Assessment, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'first_seen', 'last_activity', 'total_conversations', 'total_assessments']
    list_filter = ['first_seen', 'last_activity']
    search_fields = ['user_id']
    readonly_fields = ['first_seen', 'last_activity']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'created_at', 'updated_at', 'is_active']
    list_filter = ['created_at', 'is_active']
    search_fields = ['user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'mood_detected', 'crisis_detected', 'timestamp']
    list_filter = ['mood_detected', 'crisis_detected', 'timestamp']
    search_fields = ['session__user_id', 'user_message']
    readonly_fields = ['id', 'timestamp']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'mood', 'timestamp']
    list_filter = ['mood', 'timestamp']
    search_fields = ['session__user_id', 'context']
    readonly_fields = ['id', 'timestamp']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'assessment_type', 'total_score', 'timestamp']
    list_filter = ['assessment_type', 'timestamp']
    search_fields = ['session__user_id']
    readonly_fields = ['id', 'timestamp']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')