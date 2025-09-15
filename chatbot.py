import openai
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

class MindMateChatbot:
    def __init__(self, api_key: str):
        """Initialize the MindMate mental health chatbot."""
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = []
        self.user_mood_tracking = {}
        self.last_suggestion_type = None
        self.last_suggestion_timestamp = None

    def get_system_prompt(self) -> str:
        """Return the system prompt for mental health conversations."""
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

    def detect_crisis_keywords(self, message: str) -> bool:
        """Detect if the message contains crisis-related keywords."""
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
            'anxious': r'\b(anxious|worried|nervous|panic|stress|overwhelmed)\b',
            'depressed': r'\b(sad|depressed|down|low|empty|hopeless)\b',
            'angry': r'\b(angry|mad|furious|irritated|frustrated)\b',
            'happy': r'\b(happy|good|great|excited|joy|positive)\b',
            'confused': r'\b(confused|lost|uncertain|unclear)\b'
        }

        message_lower = message.lower()
        for mood, pattern in mood_patterns.items():
            if re.search(pattern, message_lower):
                return mood
        return None

    def track_user_mood(self, mood: str):
        """Track user's mood over time."""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.user_mood_tracking:
            self.user_mood_tracking[today] = []
        self.user_mood_tracking[today].append({
            'mood': mood,
            'timestamp': datetime.now().isoformat()
        })

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
**Reframe**: Ask "Will this matter in 5 years? What can I control?"""""
        }

        return strategies.get(mood, "Let's explore some general coping strategies that might help.")

    def analyze_assessment_results(self, assessment_type: str, score: int, responses: List[int] = None) -> str:
        """Analyze assessment results from external API."""
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

    def enhance_response_with_suggestions(self, bot_response: str, user_message: str) -> str:
        """Post-process bot response to add intelligent suggestions when appropriate."""
        enhanced_response = bot_response

        # Check if user is sharing assessment scores
        score_analysis = self._detect_and_analyze_scores(user_message)
        if score_analysis:
            enhanced_response += f"\n\n{score_analysis}"
            self._update_suggestion_history('results')

        # Add assessment suggestions
        elif self._should_suggest_assessment(user_message, bot_response):
            assessment_type = self._determine_assessment_type(user_message, bot_response)
            suggestion = self._get_assessment_suggestion(assessment_type)
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('assessment')

        # Add mood tracking suggestions
        elif self._should_suggest_mood_summary(user_message, bot_response):
            suggestion = self._get_mood_summary_suggestion()
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('mood')

        # Add result analysis suggestions
        elif self._should_suggest_result_analysis(user_message, bot_response):
            suggestion = self._get_result_analysis_suggestion()
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('results')

        return enhanced_response

    def _should_suggest_assessment(self, user_msg: str, bot_response: str) -> bool:
        """Determine if we should suggest an assessment."""
        # Don't suggest if already suggested recently
        if self._recently_suggested('assessment'):
            return False

        # Don't suggest if user just declined
        decline_words = ['no thanks', 'not interested', 'maybe later', 'not now', 'no']
        if any(word in user_msg.lower() for word in decline_words):
            return False

        # Don't suggest if already in crisis mode
        if '988' in bot_response or 'crisis' in bot_response.lower() or 'emergency' in bot_response.lower():
            return False

        # Suggest if user mentions specific symptoms
        symptom_patterns = [
            r'\b(anxious|worried|stressed|overwhelmed|panic)\b',
            r'\b(sad|depressed|down|hopeless|empty|worthless)\b',
            r'\b(not sure how.*feel|uncertain about|confused about.*mood)\b',
            r'\b(been feeling|having trouble|struggling with)\b',
            r'\b(can\'t cope|hard to handle|too much)\b'
        ]

        user_lower = user_msg.lower()
        return any(re.search(pattern, user_lower) for pattern in symptom_patterns)

    def _should_suggest_mood_summary(self, user_msg: str, bot_response: str) -> bool:
        """Determine if we should suggest mood summary."""
        if self._recently_suggested('mood'):
            return False

        # Suggest if user asks about patterns, progress, or tracking
        mood_summary_patterns = [
            r'\b(how.*been.*feeling|pattern|progress|track|over time)\b',
            r'\b(getting better|getting worse|changing|improving)\b',
            r'\b(last week|past few days|recently|lately)\b'
        ]

        user_lower = user_msg.lower()
        has_mood_data = len(self.user_mood_tracking) > 0

        return has_mood_data and any(re.search(pattern, user_lower) for pattern in mood_summary_patterns)

    def _should_suggest_result_analysis(self, user_msg: str, bot_response: str) -> bool:
        """Determine if we should suggest result analysis."""
        if self._recently_suggested('results'):
            return False

        # Check if user is sharing actual scores
        score_patterns = [
            r'\b(score.*\d+|got.*\d+|result.*\d+|\d+.*score)\b',
            r'\b(phq.*\d+|gad.*\d+)\b'
        ]

        user_lower = user_msg.lower()
        if any(re.search(pattern, user_lower) for pattern in score_patterns):
            # User is sharing actual scores - analyze them immediately
            return False  # We'll handle this differently

        # Suggest if user mentions taking assessments but hasn't shared scores
        result_patterns = [
            r'\b(took.*test|completed.*assessment|got.*results|external)\b',
            r'\b(depression.*test|anxiety.*test|mental.*health.*screening)\b',
            r'\b(therapist gave|doctor gave|online.*assessment)\b'
        ]

        return any(re.search(pattern, user_lower) for pattern in result_patterns)

    def _determine_assessment_type(self, user_msg: str, bot_response: str) -> str:
        """Determine which assessment to suggest based on context."""
        anxiety_keywords = ['anxious', 'worried', 'stress', 'nervous', 'panic', 'overwhelmed']
        depression_keywords = ['sad', 'depressed', 'down', 'hopeless', 'empty', 'worthless']

        user_lower = user_msg.lower()

        anxiety_score = sum(1 for keyword in anxiety_keywords if keyword in user_lower)
        depression_score = sum(1 for keyword in depression_keywords if keyword in user_lower)

        if anxiety_score > depression_score:
            return 'anxiety'
        elif depression_score > anxiety_score:
            return 'depression'
        else:
            return 'general'  # Offer both

    def _get_assessment_suggestion(self, assessment_type: str) -> str:
        """Generate contextual assessment suggestion with direct links."""
        from assessment_api import AssessmentAPIClient

        client = AssessmentAPIClient()

        if assessment_type == 'anxiety':
            link = client.get_assessment_link('gad7')
            return f"""**Quick Suggestion**: Since you mentioned feeling anxious, here's a GAD-7 anxiety screening that might help: {link}

This brief questionnaire can help you better understand your anxiety levels. After completing it, feel free to share your results with me and I'll help you understand what they mean."""

        elif assessment_type == 'depression':
            link = client.get_assessment_link('phq9')
            return f"""**Quick Suggestion**: It sounds like you're going through a difficult time. Here's a PHQ-9 depression screening that might help: {link}

This assessment can help clarify how you're feeling and could be useful information to share with a healthcare provider. I can help you interpret the results afterward."""

        else:  # general
            phq9_link = client.get_assessment_link('phq9')
            gad7_link = client.get_assessment_link('gad7')
            return f"""**Quick Suggestion**: Here are some mental health screenings that might help you understand your current well-being:

• **Depression (PHQ-9)**: {phq9_link}
• **Anxiety (GAD-7)**: {gad7_link}

After completing either assessment, I can help you understand your results and what they might mean."""

    def _get_mood_summary_suggestion(self) -> str:
        """Generate mood summary suggestion."""
        # Generate actual mood summary instead of asking user to type command
        mood_data = self.get_mood_summary()
        if mood_data:
            summary_text = "**Your Recent Mood Patterns**:\n"
            for date, moods in mood_data.items():
                mood_list = [m['mood'] for m in moods]
                summary_text += f"• {date}: {', '.join(mood_list)}\n"
            summary_text += "\nI notice you're asking about your mood patterns. This is what I've observed during our conversations."
            return summary_text
        else:
            return "**Mood Tracking**: I haven't tracked enough mood data yet, but I'm paying attention to how you're feeling during our conversations to help identify patterns over time."

    def _get_result_analysis_suggestion(self) -> str:
        """Generate result analysis suggestion."""
        return """**Assessment Analysis**: I'd be happy to help you understand those assessment results! You can share your scores with me like this:

"I got a score of 12 on the PHQ-9" or "My GAD-7 result was 8"

I can then explain what these numbers mean and provide personalized insights about your mental health screening."""

    def _detect_and_analyze_scores(self, user_message: str) -> Optional[str]:
        """Detect if user is sharing assessment scores and analyze them."""
        user_lower = user_message.lower()

        # Look for PHQ-9 scores
        phq_patterns = [
            r'\b(?:phq.*?(\d+)|(\d+).*?phq)\b',
            r'\b(?:depression.*?score.*?(\d+)|(\d+).*?depression.*?score)\b'
        ]

        # Look for GAD-7 scores
        gad_patterns = [
            r'\b(?:gad.*?(\d+)|(\d+).*?gad)\b',
            r'\b(?:anxiety.*?score.*?(\d+)|(\d+).*?anxiety.*?score)\b'
        ]

        # General score patterns
        general_patterns = [
            r'\b(?:score.*?(\d+)|got.*?(\d+)|result.*?(\d+))\b'
        ]

        # Check for PHQ-9
        for pattern in phq_patterns:
            match = re.search(pattern, user_lower)
            if match:
                score = int([g for g in match.groups() if g][0])
                if 0 <= score <= 27:  # Valid PHQ-9 range
                    return self.analyze_assessment_results('phq9', score)

        # Check for GAD-7
        for pattern in gad_patterns:
            match = re.search(pattern, user_lower)
            if match:
                score = int([g for g in match.groups() if g][0])
                if 0 <= score <= 21:  # Valid GAD-7 range
                    return self.analyze_assessment_results('gad7', score)

        # Check for general scores with context clues
        for pattern in general_patterns:
            match = re.search(pattern, user_lower)
            if match:
                score = int([g for g in match.groups() if g][0])

                # Determine type based on context
                if any(word in user_lower for word in ['depression', 'sad', 'down', 'phq']):
                    if 0 <= score <= 27:
                        return self.analyze_assessment_results('phq9', score)
                elif any(word in user_lower for word in ['anxiety', 'anxious', 'worried', 'gad']):
                    if 0 <= score <= 21:
                        return self.analyze_assessment_results('gad7', score)

        return None

    def _recently_suggested(self, suggestion_type: str) -> bool:
        """Check if we suggested this type recently."""
        if not self.last_suggestion_timestamp or self.last_suggestion_type != suggestion_type:
            return False

        # Don't suggest same type within last 5 exchanges
        current_exchange = len(self.conversation_history)
        last_suggestion_exchange = getattr(self, 'last_suggestion_exchange', 0)

        return (current_exchange - last_suggestion_exchange) < 10

    def _update_suggestion_history(self, suggestion_type: str):
        """Update suggestion history."""
        self.last_suggestion_type = suggestion_type
        self.last_suggestion_timestamp = datetime.now()
        self.last_suggestion_exchange = len(self.conversation_history)

    def chat(self, user_message: str) -> str:
        """Process user message and return chatbot response."""
        # Check for crisis situations first
        if self.detect_crisis_keywords(user_message):
            return self.get_crisis_response()

        # Track mood if detected
        mood = self.extract_mood_indicators(user_message)
        if mood:
            self.track_user_mood(mood)

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Prepare messages for API call
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ] + self.conversation_history[-10:]  # Keep last 10 exchanges

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content

            # Add bot response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })

            # Add coping strategies if mood detected
            if mood and mood in ['anxious', 'depressed', 'angry']:
                bot_response += f"\n\n{self.get_coping_strategy(mood)}"

            # Post-process response to add intelligent suggestions
            enhanced_response = self.enhance_response_with_suggestions(bot_response, user_message)

            return enhanced_response

        except Exception as e:
            return f"I'm having trouble connecting right now. Please try again in a moment. If you're in crisis, please call 988 for immediate support."

    def get_mood_summary(self) -> Dict:
        """Return summary of tracked moods."""
        return self.user_mood_tracking

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []