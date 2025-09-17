"""
URL patterns for MindMate chatbot app - External Backend
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='chat-health'),

    # Chat endpoints
    path('chat/', views.chat_endpoint, name='chat-endpoint'),
    path('chat/new/', views.create_new_session, name='create-new-session'),
    path('chat/history/', views.get_all_sessions, name='get-all-sessions'),
    path('chat/history/<uuid:session_id>/', views.get_session_conversations, name='get-session-conversations'),

    # Assessment endpoints
    path('assessments/', views.submit_assessment, name='submit-assessment'),

    # User endpoints
    path('users/<str:user_id>/', views.get_user_profile, name='get-user-profile'),
    path('users/<str:user_id>/assessments/', views.get_user_assessments, name='get-user-assessments'),
    path('users/<str:user_id>/moods/', views.get_user_mood_history, name='get-user-mood-history'),

    # Session endpoints
    path('sessions/<uuid:session_id>/', views.get_session_summary, name='get-session-summary'),
]