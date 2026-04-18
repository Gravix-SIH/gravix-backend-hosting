from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authentication import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ChatSession, ChatMessage, MoodEntry
import uuid
import re
from datetime import datetime
from decouple import config
from openai import OpenAI

# Initialize Groq client
_client = None

User = get_user_model()


def get_client():
    """Get or initialize Groq client."""
    global _client
    if _client is None:
        api_key = config('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    return _client


def get_session_owner(request):
    """
    Determine the owner identity for a chat session from the request.
    Returns (user_id, anonymous_id) tuple.

    If a valid JWT Bearer token is present in the Authorization header,
    uses the authenticated user. Otherwise falls back to anonymous_id
    from request body/params for unauthenticated/anonymous users.
    """
    user_id = None
    anonymous_id = None

    auth_header = request.headers.get('Authorization', '')

    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user_id = validated_token.get('user_id')
        except Exception:
            # Token invalid or expired — fall back to anonymous_id
            pass

    if not user_id:
        # Fall back to anonymous_id from request
        anonymous_id = request.data.get('anonymous_id') or request.query_params.get('anonymous_id')

    return user_id, anonymous_id


def get_user_sessions(request):
    """
    Get all ChatSession instances owned by the current user or anonymous_id.
    """
    user_id, anonymous_id = get_session_owner(request)

    if user_id:
        return ChatSession.objects.filter(user_id=user_id)
    elif anonymous_id:
        return ChatSession.objects.filter(anonymous_id=anonymous_id, user__isnull=True)
    else:
        # No identity — return empty queryset
        return ChatSession.objects.none()

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for API client."""
    return Response({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_session(request, session_id):
    """Delete a chat session. Only the owner can delete their session."""
    try:
        sessions = get_user_sessions(request)
        session = sessions.get(session_id=session_id)
        session.delete()
        return Response({'status': 'deleted', 'session_id': str(session_id)})
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        return Response({'error': 'Failed to delete session'}, status=500)

def detect_crisis(user_message):
    """Detect crisis keywords in user message."""
    crisis_keywords = [
        r'\b(kill myself|suicide|end my life|want to die|hurt myself|self.?harm)\b',
        r'\b(can\'?t go on|nothing matters|hopeless|worthless)\b',
        r'\b(commit suicide|take my life|end it all)\b'
    ]
    return any(re.search(pattern, user_message.lower()) for pattern in crisis_keywords)

def detect_emotion(user_message):
    """Detect emotion from user message."""
    emotion_patterns = {
        'anxious': r'\b(anxious|anxiety|worried|nervous|stressed|overwhelmed|panic)\b',
        'sad': r'\b(sad|depressed|down|blue|unhappy|hopeless|miserable|lonely)\b',
        'angry': r'\b(angry|mad|furious|irritated|annoyed|frustrated|resentful)\b',
        'happy': r'\b(happy|good|great|excellent|wonderful|joy|excited|glad)\b',
        'fear': r'\b(afraid|scared|frightened|terrified|panic|horror|dread)\b',
        'confused': r'\b(confused|lost|uncertain|unclear|puzzled|perplexed)\b',
        'calm': r'\b(calm|peaceful|relaxed|serene|content|satisfied)\b',
        'tired': r'\b(tired|exhausted|drained|sleepy|fatigued|weary)\b'
    }
    user_lower = user_message.lower()
    detected = []
    for emotion, pattern in emotion_patterns.items():
        if re.search(pattern, user_lower):
            detected.append(emotion)
    return detected[0] if detected else 'neutral'

def build_messages(user_message, conversation_context):
    """Build the messages list for the LLM chat completion."""
    system_prompt = """You are MindMate, a supportive mental health chatbot.
Be empathetic, warm, and non-judgmental. Provide emotional support and encourage positive coping strategies.
Never provide medical diagnoses. If someone seems to need professional help, gently suggest they consider talking to a counselor.
Keep responses concise (2-3 sentences max) and supportive.
Always respond as if you are a caring friend."""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in conversation_context:
        role = "user" if msg['role'] == 'user' else "assistant"
        messages.append({"role": role, "content": msg['content']})

    messages.append({"role": "user", "content": user_message})
    return messages


def detect_emotion_via_llm(client, user_message):
    """Detect emotion using LLM for better accuracy."""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an emotion detector. Respond with ONLY one word: sad, happy, anxious, angry, fear, tired, confused, calm, or neutral. Based on the user's message, what emotion are they expressing?"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=10,
            temperature=0.1,
        )
        emotion = response.choices[0].message.content.strip().lower()
        valid_emotions = ['sad', 'happy', 'anxious', 'angry', 'fear', 'tired', 'confused', 'calm', 'neutral']
        return emotion if emotion in valid_emotions else 'neutral'
    except Exception:
        return 'neutral'


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

        user_id, _ = get_session_owner(request)

        # Get or create session with ownership check
        session = None
        if session_id:
            sessions = get_user_sessions(request)
            try:
                session = sessions.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                pass

        if not session:
            # Check if a session with this session_id already exists in the DB
            # (it may belong to another user — reject it)
            if session_id:
                if ChatSession.objects.filter(session_id=session_id).exists():
                    return Response(
                        {'error': 'Session not found or access denied'},
                        status=403
                    )
            # Create new session owned by the current user/anonymous_id
            session = ChatSession.objects.create(
                session_id=uuid.uuid4() if not session_id else session_id,
                user_id=user_id if user_id else None,
                anonymous_id=anonymous_id if not user_id else None
            )

        # Save user message
        ChatMessage.objects.create(
            session=session,
            sender='user',
            message=user_message
        )

        # Get conversation history for context
        all_recent = list(ChatMessage.objects.filter(session=session).order_by('-timestamp')[:11])
        recent_messages = all_recent[1:] if len(all_recent) > 1 else []  # Exclude the message just saved
        conversation_context = []
        for msg in reversed(recent_messages):
            role = "user" if msg.sender == "user" else "assistant"
            conversation_context.append({"role": role, "content": msg.message})

        # Crisis detection
        is_crisis = detect_crisis(user_message)

        if is_crisis:
            crisis_response = """I'm really concerned about you right now. Your feelings are important, and there are people who want to help.

**Immediate Support:**
- Call 988 (Suicide & Crisis Lifeline) - Available 24/7
- Text "HELLO" to 741741 (Crisis Text Line)
- Go to your nearest emergency room

**You are not alone.** Please reach out to someone right now - a friend, family member, counselor, or one of these crisis services. Your life has value and meaning.

Would you like me to help you find local mental health resources or talk about what you're going through?"""

            ChatMessage.objects.create(
                session=session,
                sender='bot',
                message=crisis_response
            )

            return Response({
                'crisis': True,
                'emotion': detect_emotion(user_message),
                'reply': crisis_response,
                'session_id': str(session.session_id)
            })

        # Generate response using Groq API
        try:
            client = get_client()
            messages = build_messages(user_message, conversation_context)

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=100,
                temperature=0.7,
            )

            bot_response = response.choices[0].message.content.strip()

            # Detect emotion using LLM for accuracy
            detected_mood = detect_emotion_via_llm(client, user_message)

        except Exception as e:
            import traceback
            traceback.print_exc()
            bot_response = "I'm here to listen and support you. Your feelings are valid and important."
            detected_mood = 'neutral'

        # Save bot response
        ChatMessage.objects.create(
            session=session,
            sender='bot',
            message=bot_response,
            mood=detected_mood
        )

        # Save mood entry
        MoodEntry.objects.create(
            session=session,
            mood=detected_mood,
            intensity=5
        )

        return Response({
            'crisis': False,
            'emotion': detected_mood,
            'reply': bot_response,
            'session_id': str(session.session_id)
        })

    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'crisis': False,
            'emotion': 'neutral',
            'reply': "I'm having some technical difficulties, but I'm here for you. Please try again."
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_history(request, session_id):
    """Get conversation history for a session. Only the owner can access."""
    try:
        sessions = get_user_sessions(request)
        session = sessions.get(session_id=session_id)
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
    """Get mood summary for a session. Only the owner can access."""
    try:
        sessions = get_user_sessions(request)
        session = sessions.get(session_id=session_id)
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

@api_view(['POST'])
@permission_classes([AllowAny])
def create_new_session(request):
    """Create a new chat session and return session ID."""
    try:
        user_id, anonymous_id = get_session_owner(request)

        session = ChatSession.objects.create(
            session_id=uuid.uuid4(),
            user_id=user_id if user_id else None,
            anonymous_id=anonymous_id if not user_id else None
        )

        return Response({
            'session_id': str(session.session_id),
            'status': 'created',
            'timestamp': session.created_at.isoformat()
        })

    except Exception as e:
        return Response({
            'error': 'Failed to create session',
            'status': 'error'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_sessions(request):
    """Get all chat sessions owned by the current user/anonymous_id with their titles and last active time."""
    try:
        sessions = get_user_sessions(request).order_by('-updated_at')
        session_list = []

        for session in sessions:
            first_message = ChatMessage.objects.filter(
                session=session,
                sender='user'
            ).order_by('timestamp').first()

            last_message = ChatMessage.objects.filter(session=session).order_by('-timestamp').first()

            title = first_message.message if first_message else "New Chat"
            if len(title) > 50:
                title = title[:47] + "..."

            last_active = last_message.timestamp if last_message else session.created_at

            session_list.append({
                'session_id': str(session.session_id),
                'title': title,
                'created_at': session.created_at.isoformat(),
                'last_active': last_active.isoformat()
            })

        return Response({
            'sessions': session_list,
            'total_count': len(session_list)
        })

    except Exception as e:
        return Response({
            'error': 'Failed to fetch sessions',
            'sessions': []
        }, status=500)
