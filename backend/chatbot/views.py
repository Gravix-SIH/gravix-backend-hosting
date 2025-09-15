"""
API Views for MindMate Chatbot
"""
from rest_framework import status
from rest_framework.decorators import api_view
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

logger = logging.getLogger('chatbot')


@api_view(['POST'])
def chat(request):
    """
    Handle chat message and return bot response
    POST /api/chat/
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
def submit_assessment(request):
    """
    Submit assessment responses and get analysis
    POST /api/assessments/
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


@api_view(['GET'])
def get_user_profile(request, user_id):
    """
    Get user profile information
    GET /api/users/{user_id}/
    """
    try:
        profile = get_object_or_404(UserProfile, user_id=user_id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_session_summary(request, session_id):
    """
    Get session summary with recent conversations and moods
    GET /api/sessions/{session_id}/
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


@api_view(['GET'])
def get_user_assessments(request, user_id):
    """
    Get all assessments for a user
    GET /api/users/{user_id}/assessments/
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
def get_user_mood_history(request, user_id):
    """
    Get mood history for a user
    GET /api/users/{user_id}/moods/
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
def health_check(request):
    """
    Health check endpoint
    GET /api/health/
    """
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)