"""
API Views for MindMate Chatbot - External Backend
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatSession, UserProfile, Assessment, MoodEntry
from .serializers import (
    ChatRequestSerializer, ChatResponseSerializer,
    AssessmentSerializer, AssessmentRequestSerializer,
    UserProfileSerializer, SessionSummarySerializer,
    MoodEntrySerializer
)
from .services import ChatbotService, AssessmentService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    GET /api/v1/chatbot/health/
    """
    return Response({'status': 'healthy', 'timestamp': datetime.now().isoformat()}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_endpoint(request):
    """
    Handle chat message and return bot response
    POST /api/v1/chatbot/chat/
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    message = serializer.validated_data['message']
    user_id = serializer.validated_data.get('user_id', 'anonymous')
    session_id = serializer.validated_data.get('session_id')

    try:
        # Initialize chatbot service
        chatbot_service = ChatbotService()

        # Get or create session
        session = chatbot_service.get_or_create_session(user_id, session_id)

        # Process message
        result = chatbot_service.process_chat_message(message, session)

        logger.info(f"Chat processed for user {user_id}, session {session.id}")

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_assessment(request):
    """
    Submit assessment responses and get analysis
    POST /api/v1/chatbot/assessments/
    """
    serializer = AssessmentRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    assessment_type = serializer.validated_data['assessment_type']
    responses = serializer.validated_data['responses']
    user_id = serializer.validated_data.get('user_id', 'anonymous')
    session_id = serializer.validated_data.get('session_id')

    # Validate response count
    expected_count = 9 if assessment_type == 'phq9' else 7
    if len(responses) != expected_count:
        return Response(
            {'error': f'{assessment_type.upper()} requires exactly {expected_count} responses'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get or create session
        chatbot_service = ChatbotService()
        session = chatbot_service.get_or_create_session(user_id, session_id)

        # Process assessment
        assessment_service = AssessmentService()
        assessment = assessment_service.process_assessment(assessment_type, responses, session)

        # Serialize and return results
        serializer = AssessmentSerializer(assessment)
        logger.info(f"Assessment {assessment_type} submitted for user {user_id}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error processing assessment: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_new_session(request):
    """
    Create a new chat session
    POST /api/v1/chatbot/chat/new/
    """
    try:
        user_id = request.data.get('user_id', 'anonymous')

        # Create new session
        session = ChatSession.objects.create(user_id=user_id)

        return Response({
            'session_id': str(session.id),
            'status': 'created',
            'timestamp': session.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return Response({
            'error': 'Failed to create session',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sessions(request):
    """
    Get all chat sessions with titles (first user message)
    GET /api/v1/chatbot/chat/history/
    """
    try:
        user_id = request.GET.get('user_id', 'anonymous')

        # Get all sessions for user
        sessions = ChatSession.objects.filter(user_id=user_id).order_by('-created_at')

        session_list = []
        for session in sessions:
            # Get first conversation as title
            first_conversation = session.conversations.order_by('timestamp').first()

            title = first_conversation.user_message if first_conversation else "New Chat"
            # Truncate title if too long
            if len(title) > 50:
                title = title[:47] + "..."

            session_list.append({
                'session_id': str(session.id),
                'title': title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })

        return Response({
            'sessions': session_list,
            'total_count': len(session_list)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        return Response({
            'error': 'Failed to fetch sessions',
            'sessions': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_session_conversations(request, session_id):
    """
    Get all conversations for a specific session
    GET /api/v1/chatbot/chat/history/{session_id}/
    """
    try:
        session = get_object_or_404(ChatSession, id=session_id)
        conversations = session.conversations.order_by('timestamp')

        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                'user_message': conv.user_message,
                'bot_response': conv.bot_response,
                'mood_detected': conv.mood_detected,
                'crisis_detected': conv.crisis_detected,
                'timestamp': conv.timestamp.isoformat()
            })

        return Response({
            'session_id': str(session.id),
            'conversations': conversation_list,
            'created_at': session.created_at.isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting session conversations: {str(e)}")
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request, user_id):
    """
    Get user profile information
    GET /api/v1/chatbot/users/{user_id}/
    """
    try:
        profile, created = UserProfile.objects.get_or_create(
            user_id=user_id,
            defaults={'total_conversations': 0, 'total_assessments': 0}
        )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_mood_history(request, user_id):
    """
    Get mood history for a user
    GET /api/v1/chatbot/users/{user_id}/moods/
    """
    try:
        # Get all sessions for user
        sessions = ChatSession.objects.filter(user_id=user_id)

        # Get mood entries for these sessions
        mood_entries = MoodEntry.objects.filter(session__in=sessions).order_by('-timestamp')

        # Limit to last 50 entries
        mood_entries = mood_entries[:50]

        serializer = MoodEntrySerializer(mood_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting user mood history: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_assessments(request, user_id):
    """
    Get all assessments for a user
    GET /api/v1/chatbot/users/{user_id}/assessments/
    """
    try:
        # Get all sessions for user
        sessions = ChatSession.objects.filter(user_id=user_id)

        # Get all assessments for these sessions
        assessments = Assessment.objects.filter(session__in=sessions).order_by('-timestamp')

        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting user assessments: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_session_summary(request, session_id):
    """
    Get session summary with recent conversations and moods
    GET /api/v1/chatbot/sessions/{session_id}/
    """
    try:
        session = get_object_or_404(ChatSession, id=session_id)

        # Get recent conversations (last 10)
        recent_conversations = session.conversations.order_by('-timestamp')[:10]

        # Get recent mood entries (last 20)
        recent_moods = session.mood_entries.order_by('-timestamp')[:20]

        data = {
            'session': {
                'id': session.id,
                'user_id': session.user_id,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
            },
            'recent_conversations': [
                {
                    'id': conv.id,
                    'user_message': conv.user_message,
                    'bot_response': conv.bot_response,
                    'mood_detected': conv.mood_detected,
                    'crisis_detected': conv.crisis_detected,
                    'timestamp': conv.timestamp
                }
                for conv in recent_conversations
            ],
            'recent_moods': [
                {
                    'id': mood.id,
                    'mood': mood.mood,
                    'context': mood.context,
                    'timestamp': mood.timestamp
                }
                for mood in recent_moods
            ]
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting session summary: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
