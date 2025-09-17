from django.urls import path
from .views import health_check, chat_endpoint, conversation_history, mood_summary, create_new_session, get_all_sessions

urlpatterns = [
    path('health/', health_check, name='chat-health'),
    path('chat/', chat_endpoint, name='chat-endpoint'),
    path('chat/new/', create_new_session, name='create-new-session'),
    path('chat/history/', get_all_sessions, name='get-all-sessions'),
    path('chat/history/<str:session_id>/', conversation_history, name='conversation-history'),
    path('chat/mood/<str:session_id>/', mood_summary, name='mood-summary'),
]