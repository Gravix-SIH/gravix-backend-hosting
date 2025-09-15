"""
URL patterns for chatbot app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Chat endpoints
    path('chat/', views.chat, name='chat'),

    # Assessment endpoints
    path('assessments/', views.submit_assessment, name='submit_assessment'),

    # User endpoints
    path('users/<str:user_id>/', views.get_user_profile, name='get_user_profile'),
    path('users/<str:user_id>/assessments/', views.get_user_assessments, name='get_user_assessments'),
    path('users/<str:user_id>/moods/', views.get_user_mood_history, name='get_user_mood_history'),

    # Session endpoints
    path('sessions/<uuid:session_id>/', views.get_session_summary, name='get_session_summary'),

    # Health check
    path('health/', views.health_check, name='health_check'),
]