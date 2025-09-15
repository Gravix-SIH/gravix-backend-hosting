"""
Enhanced MindMate Chatbot with Database Integration
This version is ready for backend integration while maintaining backward compatibility
"""

import openai
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from session_manager import SessionManager, UserSession

class EnhancedMindMateChatbot:
    """Enhanced chatbot with session management and database integration."""

    def __init__(self, api_key: str, use_backend: bool = False, **db_kwargs):
        """Initialize the enhanced MindMate chatbot."""
        self.client = openai.OpenAI(api_key=api_key)
        self.session_manager = SessionManager(use_backend, **db_kwargs)
        self.current_session: Optional[UserSession] = None

    def start_session(self, user_id: str = None) -> UserSession:
        """Start a new user session."""
        self.current_session = self.session_manager.create_session(user_id)
        return self.current_session

    def get_system_prompt(self, session: UserSession = None) -> str:
        """Return the system prompt with user context."""
        base_prompt = """You are MindMate, a supportive mental health chatbot. Your purpose is to:
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

        if session:
            context = session.build_full_context()
            if context:
                return base_prompt + "\n\n" + context
            elif session.is_returning_user():
                return base_prompt + "\n\nThis is a returning user. Welcome them back warmly."

        return base_prompt

    def detect_crisis_keywords(self, message: str) -> bool:
        """Detect if the message contains crisis-related keywords."""
        crisis_patterns = [
            r'\b(suicide|kill myself|end it all|want to die|hurt myself)\b',
            r'\b(self harm|cutting|overdose)\b',
            r'\b(hopeless|worthless|no point)\b',
            r'\b(can\'t go on|no reason to live|better off dead)\b',
            r'\b(planning to die|want to disappear|tired of living)\b'
        ]

        message_lower = message.lower()
        for pattern in crisis_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    def get_crisis_response(self) -> str:
        """Return crisis intervention response."""
        return """I'm very concerned about what you're sharing. Your life has value and there are people who want to help.

**Immediate Crisis Resources:**
- **National Suicide Prevention Lifeline: 988**
- **Crisis Text Line: Text HOME to 741741**
- **Emergency Services: 911**

Please reach out to one of these resources right now. You don't have to go through this alone.

If you're in immediate danger, please call 911 or go to your nearest emergency room.

Would you like me to help you find local mental health resources or talk about what's making you feel this way?"""

    def extract_mood_indicators(self, message: str) -> Optional[str]:
        """Extract mood indicators from user message."""
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

    def get_coping_strategy(self, mood: str) -> str:
        """Provide mood-specific coping strategies."""
        strategies = {
            'anxious': """Here are some techniques that might help with anxiety:

**4-7-8 Breathing**: Inhale for 4, hold for 7, exhale for 8
**Grounding (5-4-3-2-1)**: Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste
**Challenge anxious thoughts**: Ask "Is this thought realistic? What would I tell a friend?"
**Progressive muscle relaxation**: Tense and release each muscle group""",

            'depressed': """Here are some gentle strategies for low mood:

**Light exposure**: Spend time near a window or outside
**Social connection**: Reach out to one person, even briefly
**Small accomplishments**: Set one tiny, achievable goal
**Gratitude practice**: Write down 3 small things you're grateful for
**Gentle movement**: Even a 5-minute walk can help""",

            'angry': """Here are some techniques for managing anger:

**Deep breathing**: Slow, deep breaths to activate relaxation response
**Physical release**: Go for a walk, do jumping jacks, or squeeze stress ball
**Express safely**: Write in a journal or talk to trusted friend
**Cool down**: Take a break from the situation if possible
**Reframe**: Ask "Will this matter in 5 years? What can I control?""",

            'lonely': """Here are some ways to address loneliness:

**Reach out**: Send a text or call someone, even briefly
**Community spaces**: Visit library, cafe, or community center
**Online connections**: Join forums or groups aligned with your interests
**Self-compassion**: Treat yourself with the kindness you'd show a friend
**Volunteer**: Helping others can create meaningful connections""",

            'scared': """Here are some techniques for managing fear:

**Reality check**: Ask "What's the evidence? What's most likely to happen?"
**Comfort items**: Use a blanket, stuffed animal, or calming object
**Safe space**: Identify where you feel most secure
**Support network**: Reach out to trusted friends or family
**Professional help**: Consider talking to a counselor about persistent fears"""
        }

        return strategies.get(mood, "Let's explore some general coping strategies that might help.")

    def chat(self, user_message: str, session: UserSession = None) -> str:
        """Process user message and return chatbot response."""
        if not session:
            session = self.current_session

        if not session:
            raise ValueError("No active session. Call start_session() first.")

        # Check for crisis situations first
        crisis_detected = self.detect_crisis_keywords(user_message)
        if crisis_detected:
            response = self.get_crisis_response()
            session.store_conversation(user_message, response, crisis_detected=True)
            return response

        # Extract mood and store
        mood = self.extract_mood_indicators(user_message)
        if mood:
            session.store_mood(mood, context=user_message[:100])

        # Prepare messages for API call with context
        messages = [
            {"role": "system", "content": self.get_system_prompt(session)},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content

            # Add coping strategies if mood detected
            if mood and mood in ['anxious', 'depressed', 'angry', 'lonely', 'scared']:
                bot_response += f"\n\n{self.get_coping_strategy(mood)}"

            # Store conversation
            session.store_conversation(user_message, bot_response, mood_detected=mood)

            return bot_response

        except Exception as e:
            error_response = "I'm having trouble connecting right now. Please try again in a moment. If you're in crisis, please call 988 for immediate support."
            session.store_conversation(user_message, error_response)
            return error_response

    def analyze_assessment_results(self, assessment_type: str, score: int,
                                 responses: List[int] = None, session: UserSession = None) -> str:
        """Analyze assessment results and store them."""
        if not session:
            session = self.current_session

        if session and responses:
            session.store_assessment(assessment_type, score, responses)

        # Use existing analysis logic from original chatbot
        if assessment_type.lower() == 'phq9':
            return self._analyze_phq9_results(score, responses)
        elif assessment_type.lower() == 'gad7':
            return self._analyze_gad7_results(score, responses)
        else:
            return "I'm not sure how to interpret those assessment results. Please consult with a healthcare professional."

    def _analyze_phq9_results(self, score: int, responses: List[int] = None) -> str:
        """Analyze PHQ-9 results and provide interpretation."""
        if score <= 4:
            severity = "Minimal depression"
            recommendation = "Your responses suggest minimal depressive symptoms. Keep up with healthy habits like regular exercise, good sleep, and social connections."
        elif score <= 9:
            severity = "Mild depression"
            recommendation = "Your responses suggest mild depressive symptoms. Consider self-care strategies, and if symptoms persist, talking with a healthcare provider could be helpful."
        elif score <= 14:
            severity = "Moderate depression"
            recommendation = "Your responses suggest moderate depressive symptoms. I recommend discussing these results with a healthcare provider or mental health professional."
        elif score <= 19:
            severity = "Moderately severe depression"
            recommendation = "Your responses suggest moderately severe depressive symptoms. It's important to speak with a healthcare provider soon about treatment options."
        else:
            severity = "Severe depression"
            recommendation = "Your responses suggest severe depressive symptoms. Please reach out to a healthcare provider as soon as possible for support and treatment."

        # Check for suicidal ideation (question 9)
        suicide_warning = ""
        if responses and len(responses) >= 9 and responses[8] > 0:
            suicide_warning = "\n**Important**: You indicated thoughts of self-harm. Please reach out for immediate support:\n- National Suicide Prevention Lifeline: 988\n- Crisis Text Line: Text HOME to 741741\n"

        return f"""
**PHQ-9 Assessment Results Analysis**

Your total score: {score}/27
Severity level: {severity}

**My Interpretation:**
{recommendation}

{suicide_warning}
**Next Steps:**
- These results are for screening purposes only
- Consider sharing these results with a healthcare provider
- Remember that effective treatments are available
- You don't have to face this alone

Would you like me to help you find mental health resources or discuss coping strategies?"""

    def _analyze_gad7_results(self, score: int, responses: List[int] = None) -> str:
        """Analyze GAD-7 results and provide interpretation."""
        if score <= 4:
            severity = "Minimal anxiety"
            recommendation = "Your responses suggest minimal anxiety symptoms. Continue with stress management practices and healthy lifestyle habits."
        elif score <= 9:
            severity = "Mild anxiety"
            recommendation = "Your responses suggest mild anxiety symptoms. Consider relaxation techniques, regular exercise, and if symptoms interfere with daily life, discuss with a healthcare provider."
        elif score <= 14:
            severity = "Moderate anxiety"
            recommendation = "Your responses suggest moderate anxiety symptoms. I recommend discussing these results with a healthcare provider about possible treatment options."
        else:
            severity = "Severe anxiety"
            recommendation = "Your responses suggest severe anxiety symptoms. Please consider speaking with a healthcare provider soon about treatment and support options."

        return f"""
**GAD-7 Assessment Results Analysis**

Your total score: {score}/21
Severity level: {severity}

**My Interpretation:**
{recommendation}

**Next Steps:**
- These results are for screening purposes only
- Consider sharing these results with a healthcare provider
- Anxiety is very treatable with proper support
- Consider learning anxiety management techniques

Would you like me to share some anxiety coping strategies or help you find professional resources?"""

    def get_mood_summary(self, session: UserSession = None) -> Dict:
        """Return summary of tracked moods for the user."""
        if not session:
            session = self.current_session

        if session:
            return session.database.get_mood_summary(session.user_id)
        return {}

    def get_session_info(self) -> Dict:
        """Get information about current session."""
        if self.current_session:
            return self.current_session.to_dict()
        return {}

    def cleanup_sessions(self, hours: int = 24) -> int:
        """Clean up inactive sessions."""
        return self.session_manager.cleanup_inactive_sessions(hours)