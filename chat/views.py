from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from .models import ChatSession, ChatMessage, MoodEntry
import openai
import os
import uuid
import re
from datetime import datetime

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for API client."""
    return Response({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_endpoint(request):
    """Main chat endpoint that matches your API client expectations."""
    try:
        data = request.data
        user_message = data.get('message', '')
        session_id = data.get('session_id')
        anonymous_id = data.get('anonymous_id')

        if not user_message:
            return Response({'error': 'Message is required'}, status=400)

        # Get or create session
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                pass

        if not session:
            session = ChatSession.objects.create(
                session_id=uuid.uuid4() if not session_id else session_id,
                anonymous_id=anonymous_id
            )

        # Save user message
        ChatMessage.objects.create(
            session=session,
            sender='user',
            message=user_message
        )

        # Get conversation history for context
        recent_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:10]
        conversation_context = []
        for msg in reversed(recent_messages):
            role = "user" if msg.sender == "user" else "assistant"
            conversation_context.append({"role": role, "content": msg.message})

        # Crisis detection
        crisis_keywords = [
            r'\b(kill myself|suicide|end my life|want to die|hurt myself|self.?harm)\b',
            r'\b(can\'?t go on|nothing matters|hopeless|worthless)\b'
        ]

        is_crisis = any(re.search(pattern, user_message.lower()) for pattern in crisis_keywords)

        if is_crisis:
            crisis_response = """I'm really concerned about you right now. Your feelings are important, and there are people who want to help.

**Immediate Support:**
• Call 988 (Suicide & Crisis Lifeline) - Available 24/7
• Text "HELLO" to 741741 (Crisis Text Line)
• Go to your nearest emergency room

**You are not alone.** Please reach out to someone right now - a friend, family member, counselor, or one of these crisis services. Your life has value and meaning.

Would you like me to help you find local mental health resources or talk about what you're going through?"""

            # Save bot response
            ChatMessage.objects.create(
                session=session,
                sender='bot',
                message=crisis_response
            )

            return Response({
                'response': crisis_response,
                'session_id': str(session.session_id),
                'crisis_detected': True
            })

        # Generate AI response using OpenAI
        try:
            messages = [
                {"role": "system", "content": """You are MindMate, a supportive mental health chatbot.
                Be empathetic, warm, and non-judgmental. Provide emotional support and encourage positive coping strategies.
                Never provide medical diagnoses. If someone seems to need professional help, gently suggest they consider talking to a counselor.
                Keep responses concise and supportive."""}
            ] + conversation_context

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content

        except Exception as e:
            bot_response = "I'm here to listen and support you. Sometimes I have trouble with my responses, but I want you to know that your feelings are valid and important."

        # Extract mood if mentioned
        mood_patterns = {
            'anxious': r'\b(anxious|anxiety|worried|nervous|stressed)\b',
            'sad': r'\b(sad|depressed|down|blue|unhappy)\b',
            'angry': r'\b(angry|mad|furious|irritated|annoyed)\b',
            'happy': r'\b(happy|good|great|excellent|wonderful)\b',
            'confused': r'\b(confused|lost|uncertain|unclear)\b'
        }

        detected_mood = None
        for mood, pattern in mood_patterns.items():
            if re.search(pattern, user_message.lower()):
                detected_mood = mood
                break

        # Save bot response
        ChatMessage.objects.create(
            session=session,
            sender='bot',
            message=bot_response,
            mood=detected_mood
        )

        # Save mood entry if detected
        if detected_mood:
            MoodEntry.objects.create(
                session=session,
                mood=detected_mood,
                intensity=5  # Default intensity
            )

        return Response({
            'response': bot_response,
            'session_id': str(session.session_id),
            'mood_detected': detected_mood
        })

    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'response': "I'm having some technical difficulties, but I'm here for you. Please try again."
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_history(request, session_id):
    """Get conversation history for a session."""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')

        conversations = []
        for msg in messages:
            conversations.append({
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'mood': msg.mood
            })

        return Response({'conversations': conversations})

    except ChatSession.DoesNotExist:
        return Response({'conversations': []})

@api_view(['GET'])
@permission_classes([AllowAny])
def mood_summary(request, session_id):
    """Get mood summary for a session."""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        moods = MoodEntry.objects.filter(session=session).order_by('-timestamp')

        mood_data = []
        for mood in moods:
            mood_data.append({
                'mood': mood.mood,
                'intensity': mood.intensity,
                'timestamp': mood.timestamp.isoformat()
            })

        return Response({'mood_summary': mood_data})

    except ChatSession.DoesNotExist:
        return Response({'mood_summary': []})
