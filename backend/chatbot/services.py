"""
Business logic services for MindMate Chatbot
"""
import openai
import re
from typing import Optional, Dict, List, Tuple
from django.conf import settings
from .models import ChatSession, Conversation, MoodEntry, Assessment, UserProfile


class ChatbotService:
    """Service class for chatbot functionality"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_or_create_session(self, user_id: str, session_id: str = None) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user_id=user_id)
                return session
            except ChatSession.DoesNotExist:
                pass

        # Create new session
        session = ChatSession.objects.create(user_id=user_id)

        # Update or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user_id=user_id,
            defaults={'total_conversations': 0, 'total_assessments': 0}
        )

        return session

    def detect_crisis_keywords(self, message: str) -> bool:
        """Detect crisis-related keywords in user message"""
        crisis_patterns = [
            r'\b(suicide|kill myself|end it all|want to die|hurt myself)\b',
            r'\b(self harm|cutting|overdose)\b',
            r'\b(hopeless|worthless|no point)\b'
        ]

        message_lower = message.lower()
        for pattern in crisis_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    def extract_mood_indicators(self, message: str) -> Optional[str]:
        """Extract mood indicators from user message"""
        mood_patterns = {
            'anxious': r'\b(anxious|worried|nervous|panic|stress|overwhelmed|tense)\b',
            'depressed': r'\b(sad|depressed|down|low|empty|hopeless|blue)\b',
            'angry': r'\b(angry|mad|furious|irritated|frustrated|rage)\b',
            'happy': r'\b(happy|good|great|excited|joy|positive|cheerful)\b',
            'confused': r'\b(confused|lost|uncertain|unclear|mixed up)\b',
            'lonely': r'\b(lonely|alone|isolated|disconnected)\b',
            'scared': r'\b(scared|afraid|fearful|terrified|frightened)\b'
        }

        message_lower = message.lower()
        for mood, pattern in mood_patterns.items():
            if re.search(pattern, message_lower):
                return mood
        return None

    def get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are MindMate, a supportive mental health chatbot. Your purpose is to:
- Provide empathetic and safe conversations
- Encourage positive coping strategies and emotional regulation
- Escalate to crisis mode when harmful or suicidal language is detected

You are NOT a substitute for professional care and should never provide diagnoses or medical advice.

Style Guide:
- Always be empathetic, warm, and non-judgmental
- Prioritize validation ("It makes sense you feel this way") before giving suggestions
- Use short, clear sentences
- Never push; always offer choices ("Would you like to try...?")
- Focus on listening and understanding the user's feelings

Safety Rules:
- Never provide medical or diagnostic advice
- In crisis mode, prioritize safety over continuing normal conversation
- Never ignore or downplay harmful language
- Always encourage professional help when appropriate"""

    def get_crisis_response(self) -> str:
        """Get crisis response message"""
        return """I'm really concerned about you right now. Your safety is the most important thing.

**Immediate Support:**
- **National Suicide Prevention Lifeline: 988**
- **Crisis Text Line: Text HOME to 741741**
- **Emergency Services: 911**

Please reach out to one of these resources right now. You don't have to go through this alone.

If you're in immediate danger, please call 911 or go to your nearest emergency room.

Would you like me to help you find local mental health resources or talk about what's making you feel this way?"""

    def process_chat_message(self, message: str, session: ChatSession) -> Dict:
        """Process incoming chat message and return response"""
        # Check for crisis situations first
        crisis_detected = self.detect_crisis_keywords(message)
        if crisis_detected:
            response = self.get_crisis_response()

            # Store conversation
            conversation = Conversation.objects.create(
                session=session,
                user_message=message,
                bot_response=response,
                crisis_detected=True
            )

            return {
                'response': response,
                'session_id': session.id,
                'crisis_detected': True,
                'conversation_id': conversation.id
            }

        # Extract and store mood
        mood = self.extract_mood_indicators(message)
        if mood:
            MoodEntry.objects.create(
                session=session,
                mood=mood,
                context=message[:100]  # First 100 chars as context
            )

        # Get recent conversation context
        recent_conversations = session.conversations.order_by('-timestamp')[:5]
        context_messages = []

        for conv in reversed(recent_conversations):
            context_messages.extend([
                {"role": "user", "content": conv.user_message},
                {"role": "assistant", "content": conv.bot_response}
            ])

        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": message})

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content

            # Store conversation
            conversation = Conversation.objects.create(
                session=session,
                user_message=message,
                bot_response=bot_response,
                mood_detected=mood
            )

            # Update user profile
            profile = UserProfile.objects.get(user_id=session.user_id)
            profile.total_conversations += 1
            profile.save()

            return {
                'response': bot_response,
                'session_id': session.id,
                'mood_detected': mood,
                'crisis_detected': False,
                'conversation_id': conversation.id
            }

        except Exception as e:
            # Fallback response
            fallback_response = "I'm having trouble connecting right now. Please try again in a moment. If you're in crisis, please call 988 for immediate support."

            conversation = Conversation.objects.create(
                session=session,
                user_message=message,
                bot_response=fallback_response,
                mood_detected=mood
            )

            return {
                'response': fallback_response,
                'session_id': session.id,
                'mood_detected': mood,
                'crisis_detected': False,
                'conversation_id': conversation.id,
                'error': str(e)
            }


class AssessmentService:
    """Service class for assessment functionality"""

    def calculate_phq9_score(self, responses: List[int]) -> Tuple[int, str]:
        """Calculate PHQ-9 score and interpretation"""
        if len(responses) != 9:
            raise ValueError("PHQ-9 requires exactly 9 responses")

        total_score = sum(responses)

        if total_score <= 4:
            interpretation = "Minimal depression"
        elif total_score <= 9:
            interpretation = "Mild depression"
        elif total_score <= 14:
            interpretation = "Moderate depression"
        elif total_score <= 19:
            interpretation = "Moderately severe depression"
        else:
            interpretation = "Severe depression"

        return total_score, interpretation

    def calculate_gad7_score(self, responses: List[int]) -> Tuple[int, str]:
        """Calculate GAD-7 score and interpretation"""
        if len(responses) != 7:
            raise ValueError("GAD-7 requires exactly 7 responses")

        total_score = sum(responses)

        if total_score <= 4:
            interpretation = "Minimal anxiety"
        elif total_score <= 9:
            interpretation = "Mild anxiety"
        elif total_score <= 14:
            interpretation = "Moderate anxiety"
        else:
            interpretation = "Severe anxiety"

        return total_score, interpretation

    def process_assessment(self, assessment_type: str, responses: List[int], session: ChatSession) -> Assessment:
        """Process assessment submission"""
        if assessment_type == 'phq9':
            total_score, interpretation = self.calculate_phq9_score(responses)
        elif assessment_type == 'gad7':
            total_score, interpretation = self.calculate_gad7_score(responses)
        else:
            raise ValueError(f"Unknown assessment type: {assessment_type}")

        # Store assessment
        assessment = Assessment.objects.create(
            session=session,
            assessment_type=assessment_type,
            total_score=total_score,
            responses=responses,
            interpretation=interpretation
        )

        # Update user profile
        profile = UserProfile.objects.get(user_id=session.user_id)
        profile.total_assessments += 1
        profile.save()

        return assessment