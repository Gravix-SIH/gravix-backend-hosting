"""
Multilingual MindMate Chatbot with Language Support
Extends the enhanced chatbot with full multilingual capabilities
"""

import openai
import re
from typing import List, Dict, Optional
from enhanced_chatbot import EnhancedMindMateChatbot
from language_manager import LanguageManager, SupportedLanguage
from session_manager import SessionManager, UserSession

class MultilingualMindMateChatbot(EnhancedMindMateChatbot):
    """Enhanced chatbot with multilingual support."""

    def __init__(self, api_key: str, use_backend: bool = False, **db_kwargs):
        """Initialize the multilingual MindMate chatbot."""
        super().__init__(api_key, use_backend, **db_kwargs)
        self.language_manager = LanguageManager()

    def start_session(self, user_id: str = None, language: SupportedLanguage = None) -> UserSession:
        """Start a new user session with language preference."""
        session = super().start_session(user_id)

        # Check for saved language preference
        if not language and user_id:
            language = self.language_manager.load_user_language_preference(user_id)

        # If no language specified, show selection
        if not language:
            language = self.language_manager.show_language_selection()

        # Set language and save preference
        self.language_manager.set_language(language)
        if user_id:
            self.language_manager.save_user_language_preference(user_id, language)

        return session

    def get_system_prompt(self, session: UserSession = None) -> str:
        """Return the system prompt with cultural and language context."""
        base_prompt = """You are MindMate, a supportive mental health chatbot. Your purpose is to:
- Provide empathetic and safe conversations
- Encourage positive coping strategies and emotional regulation
- Escalate to crisis mode when harmful or suicidal language is detected

You are NOT a substitute for professional care and should never provide diagnoses or medical advice.

Style Guide:
- Always be empathetic, warm, and non-judgmental
- Prioritize validation before giving suggestions
- Use short, clear sentences
- Never push; always offer choices
- Focus on listening and understanding the user's feelings

Safety Rules:
- Never provide medical or diagnostic advice
- In crisis mode, prioritize safety over continuing normal conversation
- Never ignore or downplay harmful language
- Always encourage professional help when appropriate"""

        # Add cultural context and language instruction
        adapted_prompt = self.language_manager.get_system_prompt(base_prompt)

        # Add session context if available
        if session:
            context = session.build_full_context()
            if context:
                adapted_prompt += "\n\n" + context
            elif session.is_returning_user():
                returning_message = self.language_manager.get_text('welcome_back')
                adapted_prompt += f"\n\nThis is a returning user. Welcome them back warmly: {returning_message}"

        return adapted_prompt

    def detect_crisis_keywords(self, message: str) -> bool:
        """Detect crisis keywords in multiple languages."""
        # English patterns (original)
        english_patterns = [
            r'\b(suicide|kill myself|end it all|want to die|hurt myself)\b',
            r'\b(self harm|cutting|overdose)\b',
            r'\b(hopeless|worthless|no point)\b',
            r'\b(can\'t go on|no reason to live|better off dead)\b'
        ]

        # Hindi patterns
        hindi_patterns = [
            r'\b(आत्महत्या|मरना चाहता|जिंदगी से तंग|मर जाऊं)\b',
            r'\b(खुद को मारना|नुकसान पहुंचाना|काटना)\b',
            r'\b(निराश|बेकार|कोई फायदा नहीं|जीने का मतलब नहीं)\b'
        ]

        # Tamil patterns
        tamil_patterns = [
            r'\b(தற்கொலை|மரணம்|சாக வேண்டும்|உயிர் வேண்டாம்)\b',
            r'\b(தன்னை காயப்படுத்துதல்|வெட்டுதல்)\b',
            r'\b(நம்பிக்கையற்று|பயனற்று|அர்த்தம் இல்லை)\b'
        ]

        message_lower = message.lower()

        # Check all patterns
        all_patterns = english_patterns + hindi_patterns + tamil_patterns
        for pattern in all_patterns:
            if re.search(pattern, message_lower):
                return True

        return False

    def get_crisis_response(self) -> str:
        """Return localized crisis intervention response."""
        crisis_resources = self.language_manager.get_crisis_resources()

        # Build crisis response with localized resources
        base_response = """I'm very concerned about what you're sharing. Your life has value and there are people who want to help.

**Immediate Crisis Resources:**"""

        for key, resource in crisis_resources.items():
            base_response += f"\n- **{resource}**"

        base_response += """

Please reach out to one of these resources right now. You don't have to go through this alone.

If you're in immediate danger, please call emergency services or go to your nearest emergency room.

Would you like me to help you find local mental health resources or talk about what's making you feel this way?"""

        return base_response

    def extract_mood_indicators(self, message: str) -> Optional[str]:
        """Extract mood indicators in multiple languages."""
        # English patterns (original)
        english_patterns = {
            'anxious': r'\b(anxious|worried|nervous|panic|stress|overwhelmed|tense)\b',
            'depressed': r'\b(sad|depressed|down|low|empty|hopeless|blue)\b',
            'angry': r'\b(angry|mad|furious|irritated|frustrated|rage)\b',
            'happy': r'\b(happy|good|great|excited|joy|positive|cheerful)\b',
            'confused': r'\b(confused|lost|uncertain|unclear|mixed up)\b',
            'lonely': r'\b(lonely|alone|isolated|disconnected)\b',
            'scared': r'\b(scared|afraid|fearful|terrified|frightened)\b'
        }

        # Hindi patterns
        hindi_patterns = {
            'anxious': r'\b(चिंतित|परेशान|घबराया|तनाव|चिंता|डरा)\b',
            'depressed': r'\b(उदास|निराश|दुखी|अकेला|खुशी नहीं)\b',
            'angry': r'\b(गुस्सा|क्रोधित|चिढ़|नाराज|गुस्से में)\b',
            'happy': r'\b(खुश|प्रसन्न|अच्छा|खुशी|हर्षित)\b',
            'confused': r'\b(भ्रमित|समझ नहीं|उलझन|स्पष्ट नहीं)\b',
            'lonely': r'\b(अकेला|एकाकी|अलग|कोई नहीं)\b',
            'scared': r'\b(डरा|भयभीत|चिंतित|घबराया)\b'
        }

        # Tamil patterns
        tamil_patterns = {
            'anxious': r'\b(கவலை|பதற்றம்|அச்சம்|பயம்|மன அழுத்தम்)\b',
            'depressed': r'\b(மனச்சோர்வு|வருத்தம்|சோகம்|மகிழ்ச்சி இல்லை)\b',
            'angry': r'\b(கோபம்|எரிச்சல்|கோபத்தில்|கோபமாக)\b',
            'happy': r'\b(மகிழ்ச்சி|நல்லது|சந்தோஷம்|உற்சாகம்)\b',
            'confused': r'\b(குழப்பம்|புரியவில்லை|தெளிவில்லை)\b',
            'lonely': r'\b(தனிமை|தனியாக|ஒதுக்கப்பட்ட)\b',
            'scared': r'\b(பயம்|அச்சம்|பயந்து|திகில்)\b'
        }

        message_lower = message.lower()

        # Check all language patterns
        all_patterns = {**english_patterns, **hindi_patterns, **tamil_patterns}
        for mood, pattern in all_patterns.items():
            if re.search(pattern, message_lower):
                return mood

        return None

    def get_coping_strategy(self, mood: str) -> str:
        """Get culturally appropriate coping strategies."""
        return self.language_manager.get_coping_strategies(mood)

    def chat(self, user_message: str, session: UserSession = None) -> str:
        """Process user message with multilingual support."""
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

        # Prepare messages for API call with cultural context
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

            # Add culturally appropriate coping strategies if mood detected
            if mood and mood in ['anxious', 'depressed', 'angry', 'lonely', 'scared']:
                coping_strategy = self.get_coping_strategy(mood)
                if coping_strategy:
                    bot_response += f"\n\n{coping_strategy}"

            # Enhance response with intelligent suggestions (assessments, resources)
            enhanced_response = self.enhance_response_with_suggestions(bot_response, user_message, session)

            # Store conversation
            session.store_conversation(user_message, enhanced_response, mood_detected=mood)

            return enhanced_response

        except Exception as e:
            error_response = self.language_manager.get_text('api_error')
            crisis_backup = self.language_manager.get_text('crisis_backup')
            full_error = f"{error_response}\n{crisis_backup}"

            session.store_conversation(user_message, full_error)
            return full_error

    def analyze_assessment_results(self, assessment_type: str, score: int,
                                 responses: List[int] = None, session: UserSession = None) -> str:
        """Analyze assessment results with cultural context."""
        if not session:
            session = self.current_session

        if session and responses:
            session.store_assessment(assessment_type, score, responses)

        # Use culturally adapted analysis
        if assessment_type.lower() == 'phq9':
            return self._analyze_phq9_results_multilingual(score, responses)
        elif assessment_type.lower() == 'gad7':
            return self._analyze_gad7_results_multilingual(score, responses)
        else:
            return "I'm not sure how to interpret those assessment results. Please consult with a healthcare professional."

    def _analyze_phq9_results_multilingual(self, score: int, responses: List[int] = None) -> str:
        """Analyze PHQ-9 results with cultural adaptation."""
        # Determine severity level
        if score <= 4:
            severity = "minimal"
        elif score <= 9:
            severity = "mild"
        elif score <= 14:
            severity = "moderate"
        elif score <= 19:
            severity = "moderately_severe"
        else:
            severity = "severe"

        # Get culturally appropriate recommendations
        mental_health_resources = self.language_manager.get_mental_health_resources()

        # Build response with cultural context
        current_lang = self.language_manager.current_language.value

        if current_lang == "hi":
            severity_map = {
                "minimal": "न्यूनतम अवसाद",
                "mild": "हल्का अवसाद",
                "moderate": "मध्यम अवसाद",
                "moderately_severe": "मध्यम से गंभीर अवसाद",
                "severe": "गंभीर अवसाद"
            }
        elif current_lang == "ta":
            severity_map = {
                "minimal": "குறைந்தபட்ச மனச்சோர்வு",
                "mild": "லேசான மனச்சோர்வு",
                "moderate": "மிதமான மனச்சோர்வு",
                "moderately_severe": "மிதம் முதல் கடுமையான மனச்சோர்வு",
                "severe": "கடுமையான மனச்சோர்வு"
            }
        else:
            severity_map = {
                "minimal": "Minimal depression",
                "mild": "Mild depression",
                "moderate": "Moderate depression",
                "moderately_severe": "Moderately severe depression",
                "severe": "Severe depression"
            }

        severity_text = severity_map.get(severity, severity)

        # Check for suicidal ideation (question 9)
        suicide_warning = ""
        if responses and len(responses) >= 9 and responses[8] > 0:
            crisis_resources = self.language_manager.get_crisis_resources()
            suicide_warning = "\n**Important**: " + self.language_manager.get_text('crisis_backup') + "\n"
            for resource in crisis_resources.values():
                suicide_warning += f"- {resource}\n"

        # Build localized response
        if current_lang == "hi":
            result_text = f"""
**PHQ-9 मूल्यांकन परिणाम विश्लेषण**

आपका कुल स्कोर: {score}/27
गंभीरता स्तर: {severity_text}

{suicide_warning}
**अगले कदम:**
- ये परिणाम केवल स्क्रीनिंग के लिए हैं
- इन परिणामों को किसी डॉक्टर से साझा करने पर विचार करें
- याद रखें कि प्रभावी उपचार उपलब्ध हैं
- आपको अकेले इससे निपटना नहीं है

क्या आप चाहेंगे कि मैं आपको मानसिक स्वास्थ्य संसाधन खोजने में मदद करूं या मुकाबला करने की रणनीतियों पर चर्चा करूं?"""

        elif current_lang == "ta":
            result_text = f"""
**PHQ-9 மதிப்பீடு முடிவுகள் பகுப்பாய்வு**

உங்கள் மொத்த மதிப்பெண்: {score}/27
தீவிரத்தன்மை நிலை: {severity_text}

{suicide_warning}
**அடுத்த படிகள்:**
- இந்த முடிவுகள் பரிசோதனை நோக்கத்திற்காக மட்டுமே
- இந்த முடிவுகளை மருத்துவரிடம் பகிர்ந்து கொள்ளவும்
- நினைவில் கொள்ளுங்கள் பயனுள்ள சிகிச்சைகள் கிடைக்கின்றன
- நீங்கள் இதை தனியாக எதிர்கொள்ள வேண்டியதில்லை

மனநல ஆதாரங்களைக் கண்டறிய உதவ வேண்டுமா அல்லது சமாளிப்பு உத்திகளைப் பற்றி விவாதிக்க வேண்டுமா?"""

        else:  # English
            result_text = f"""
**PHQ-9 Assessment Results Analysis**

Your total score: {score}/27
Severity level: {severity_text}

{suicide_warning}
**Next Steps:**
- These results are for screening purposes only
- Consider sharing these results with a healthcare provider
- Remember that effective treatments are available
- You don't have to face this alone

Would you like me to help you find mental health resources or discuss coping strategies?"""

        return result_text

    def _analyze_gad7_results_multilingual(self, score: int, responses: List[int] = None) -> str:
        """Analyze GAD-7 results with cultural adaptation."""
        # Similar structure to PHQ-9 but for anxiety
        if score <= 4:
            severity = "minimal"
        elif score <= 9:
            severity = "mild"
        elif score <= 14:
            severity = "moderate"
        else:
            severity = "severe"

        current_lang = self.language_manager.current_language.value

        if current_lang == "hi":
            severity_map = {
                "minimal": "न्यूनतम चिंता",
                "mild": "हल्की चिंता",
                "moderate": "मध्यम चिंता",
                "severe": "गंभीर चिंता"
            }
        elif current_lang == "ta":
            severity_map = {
                "minimal": "குறைந்தபட்ச கவலை",
                "mild": "லேசான கவலை",
                "moderate": "மிதமான கவலை",
                "severe": "கடுமையான கவலை"
            }
        else:
            severity_map = {
                "minimal": "Minimal anxiety",
                "mild": "Mild anxiety",
                "moderate": "Moderate anxiety",
                "severe": "Severe anxiety"
            }

        severity_text = severity_map.get(severity, severity)

        # Build localized response (similar pattern to PHQ-9)
        if current_lang == "hi":
            result_text = f"""
**GAD-7 चिंता मूल्यांकन परिणाम विश्लेषण**

आपका कुल स्कोर: {score}/21
गंभीरता स्तर: {severity_text}

**अगले कदम:**
- ये परिणाम केवल स्क्रीनिंग के लिए हैं
- इन परिणामों को किसी डॉक्टर से साझा करने पर विचार करें
- चिंता का इलाज बहुत प्रभावी है
- चिंता प्रबंधन तकनीकें सीखने पर विचार करें

क्या आप चाहेंगे कि मैं कुछ चिंता निवारण रणनीतियां साझा करूं या आपको पेशेवर संसाधन खोजने में मदद करूं?"""

        elif current_lang == "ta":
            result_text = f"""
**GAD-7 கவலை மதிப்பீடு முடிவுகள் பகுப்பாய்வு**

உங்கள் மொத்த மதிப்பெண்: {score}/21
தீவிரத்தன்மை நிலை: {severity_text}

**அடுத்த படிகள்:**
- இந்த முடிவுகள் பரிசோதனை நோக்கத்திற்காக மட்டுமே
- இந்த முடிவுகளை மருத்துவரிடம் பகிர்ந்து கொள்ளவும்
- கவலை சிகிச்சை மிகவும் பயனுள்ளது
- கவலை மேலாண்மை நுட்பங்களைக் கற்றுக்கொள்ள வேண்டுமா

சில கவலை சமாளிப்பு உத்திகளைப் பகிர வேண்டுமா அல்லது தொழில்முறை ஆதாரங்களைக் கண்டறிய உதவ வேண்டுமா?"""

        else:  # English
            result_text = f"""
**GAD-7 Assessment Results Analysis**

Your total score: {score}/21
Severity level: {severity_text}

**Next Steps:**
- These results are for screening purposes only
- Consider sharing these results with a healthcare provider
- Anxiety is very treatable with proper support
- Consider learning anxiety management techniques

Would you like me to share some anxiety coping strategies or help you find professional resources?"""

        return result_text

    def enhance_response_with_suggestions(self, bot_response: str, user_message: str, session: UserSession) -> str:
        """Post-process bot response to add intelligent suggestions when appropriate."""
        enhanced_response = bot_response

        # Check if user is sharing assessment scores
        score_analysis = self._detect_and_analyze_scores(user_message)
        if score_analysis:
            enhanced_response += f"\n\n{score_analysis}"
            self._update_suggestion_history('results', session)

        # Add assessment suggestions
        elif self._should_suggest_assessment(user_message, bot_response, session):
            assessment_type = self._determine_assessment_type(user_message, bot_response)
            suggestion = self._get_assessment_suggestion_multilingual(assessment_type)
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('assessment', session)

        # Add mood tracking suggestions
        elif self._should_suggest_mood_summary(user_message, bot_response, session):
            suggestion = self._get_mood_summary_suggestion_multilingual(session)
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('mood', session)

        # Add result analysis suggestions
        elif self._should_suggest_result_analysis(user_message, bot_response, session):
            suggestion = self._get_result_analysis_suggestion_multilingual()
            enhanced_response += f"\n\n{suggestion}"
            self._update_suggestion_history('results', session)

        return enhanced_response

    def _should_suggest_assessment(self, user_msg: str, bot_response: str, session: UserSession) -> bool:
        """Determine if we should suggest an assessment (multilingual)."""
        # Don't suggest if already suggested recently
        if self._recently_suggested('assessment', session):
            return False

        # Don't suggest if user just declined (multilingual)
        decline_patterns = [
            # English
            r'\b(no thanks|not interested|maybe later|not now|no)\b',
            # Hindi
            r'\b(नहीं धन्यवाद|रुचि नहीं|बाद में|अभी नहीं|नहीं)\b',
            # Tamil
            r'\b(வேண்டாம் நன்றி|ஆர்வம் இல்லை|பின்னர்|இப்போது இல்லை|இல்லை)\b'
        ]

        user_lower = user_msg.lower()
        for pattern in decline_patterns:
            if re.search(pattern, user_lower):
                return False

        # Don't suggest if already in crisis mode
        if '988' in bot_response or '108' in bot_response or '112' in bot_response or 'crisis' in bot_response.lower():
            return False

        # Suggest if user mentions specific symptoms (multilingual)
        symptom_patterns = [
            # English
            r'\b(anxious|worried|stressed|overwhelmed|panic|depressed|sad|down|hopeless)\b',
            r'\b(not sure how.*feel|uncertain about|confused about.*mood)\b',
            r'\b(been feeling|having trouble|struggling with)\b',
            # Hindi
            r'\b(चिंतित|परेशान|तनावग्रस्त|घबराया|पैनिक|अवसादग्रस्त|उदास|निराश)\b',
            r'\b(समझ नहीं.*महसूस|अनिश्चित|भ्रमित.*मूड)\b',
            r'\b(महसूस कर रहा|परेशानी हो रही|संघर्ष कर रहा)\b',
            # Tamil
            r'\b(கவलை|பதற்றம்|மன அழুत्तम्|பயம்|மனச்சோर्वু|வருत्तम্|निराश)\b',
            r'\b(புரியவில्लை.*உணর्वु|अनिश्चित|குழप्पम्.*मूड)\b',
            r'\b(உணर्कிறேன्|परेशानी|போराट्टम्)\b'
        ]

        return any(re.search(pattern, user_lower) for pattern in symptom_patterns)

    def _determine_assessment_type(self, user_msg: str, bot_response: str) -> str:
        """Determine which assessment to suggest based on context (multilingual)."""
        # English keywords
        anxiety_keywords = ['anxious', 'worried', 'stress', 'nervous', 'panic', 'overwhelmed']
        depression_keywords = ['sad', 'depressed', 'down', 'hopeless', 'empty', 'worthless']

        # Hindi keywords
        anxiety_keywords.extend(['चिंतित', 'परेशान', 'तनाव', 'घबराया', 'पैनिक'])
        depression_keywords.extend(['उदास', 'अवसादग्रस्त', 'निराश', 'खाली', 'बेकार'])

        # Tamil keywords
        anxiety_keywords.extend(['கவலை', 'பதற்றம்', 'மன அழுத्तம्', 'பயம्'])
        depression_keywords.extend(['மனச्चोर्वु', 'வরुत्तम्', 'निराश', 'खाली'])

        user_lower = user_msg.lower()

        anxiety_score = sum(1 for keyword in anxiety_keywords if keyword in user_lower)
        depression_score = sum(1 for keyword in depression_keywords if keyword in user_lower)

        if anxiety_score > depression_score:
            return 'anxiety'
        elif depression_score > anxiety_score:
            return 'depression'
        else:
            return 'general'

    def _get_assessment_suggestion_multilingual(self, assessment_type: str) -> str:
        """Generate contextual assessment suggestion with cultural adaptation."""
        current_lang = self.language_manager.current_language.value

        if assessment_type == 'anxiety':
            if current_lang == "hi":
                return """**सुझाव**: चूंकि आपने चिंता का उल्लेख किया है, GAD-7 चिंता स्क्रीनिंग आपके लिए उपयोगी हो सकती है।

यह संक्षिप्त प्रश्नावली आपकी चिंता के स्तर को बेहतर ढंग से समझने में मदद कर सकती है। इसे पूरा करने के बाद, परिणाम मुझसे साझा करें और मैं आपको समझाने में मदद करूंगा कि इसका क्या मतलब है।

क्या आप चाहेंगे कि मैं आपके साथ यह छोटी सी चिंता जांच करूं? बस "हां", "जी हां", या "चलिए करते हैं" कहें।"""

            elif current_lang == "ta":
                return """**பரிந்துரை**: நீங்கள் கவலையைப் பற்றி குறிப்பிட்டதால், GAD-7 கவலை பரிசோதனை உங்களுக்கு உதவிகரமாக இருக்கலாம்।

இந்த சுருக்கமான கேள்வித்தாள் உங்கள் கவலை அளவுகளை நன்றாக புரிந்து கொள்ள உதவும். அதை முடித்த பிறகு, முடிவுகளை என்னுடன் பகிர்ந்து கொள்ளுங்கள், அவை என்ன அர்த்தம் என்பதை புரிந்து கொள்ள உதவுவேன்.

இந்த சிறிய கவலை பரிசோதனையை நான் உங்களுடன் மேற்கொள்ள வேண்டுமா? "ஆம்", "சரி", அல்லது "செய்வோம்" என்று சொல்லுங்கள்."""

            else:  # English
                return """**Quick Suggestion**: Since you mentioned feeling anxious, a GAD-7 anxiety screening might help you better understand your anxiety levels.

This brief questionnaire can help clarify how you're feeling and could be useful information to share with a healthcare provider. I can help you interpret the results afterward.

Would you like me to walk you through this assessment? Just say "yes", "sure", or "let's do it"."""

        elif assessment_type == 'depression':
            if current_lang == "hi":
                return """**सुझाव**: ऐसा लगता है कि आप कठिन समय से गुजर रहे हैं। PHQ-9 अवसाद स्क्रीनिंग आपके लिए सहायक हो सकती है।

यह मूल्यांकन स्पष्ट करने में मदद कर सकता है कि आप कैसा महसूस कर रहे हैं और स्वास्थ्य सेवा प्रदाता के साथ साझा करने के लिए उपयोगी जानकारी हो सकती है।

क्या आप चाहेंगे कि मैं आपके साथ यह छोटा सा अवसाद मूल्यांकन करूं? बस "हां" या "जी हां" कहें और हम शुरू कर सकते हैं।"""

            elif current_lang == "ta":
                return """**பரிந்துரை**: நீங்கள் கடினமான நேரத்தைக் கடந்து வருகிறீர்கள் என்று தெரிகிறது। PHQ-9 மனச்சோர்வு பரிசோதனை உங்களுக்கு உதவிகரமாக இருக்கலாம்।

இந்த மதிப்பீடு நீங்கள் எப்படி உணர்கிறீர்கள் என்பதைத் தெளிவுபடுத்த உதவும் மற்றும் சுகாதார வழங்குநருடன் பகிர்ந்து கொள்ள பயனுள்ள தகவலாக இருக்கலாம். பின்னர் முடிவுகளை விளக்க நான் உங்களுக்கு உதவ முடியும்.

இந்த சிறிய கவலை பரிசோதனையை நான் உங்களுடன் மேற்கொள்ள வேண்டுமா? "ஆம்", "சரி", அல்லது "செய்வோம்" என்று சொல்லுங்கள்."""

            else:  # English
                return """**Quick Suggestion**: It sounds like you're going through a difficult time. A PHQ-9 depression screening might help clarify how you're feeling.

This assessment can help you understand your current well-being and could be useful information to share with a healthcare provider.

Would you like me to walk you through this brief depression assessment? Just say "yes" or "sure" and we can start."""

        else:  # general
            if current_lang == "hi":
                return """**सुझाव**: यहाँ कुछ मानसिक स्वास्थ्य स्क्रीनिंग हैं जो आपकी वर्तमान भलाई को समझने में मदद कर सकती हैं:

• **अवसाद (PHQ-9)**: मूड और रुचि के स्तर का आकलन
• **चिंता (GAD-7)**: चिंता और चिंता के स्तर का आकलन

किसी भी मूल्यांकन को पूरा करने के बाद, मैं आपके परिणामों को समझने और उनका क्या मतलब हो सकता है, इसमें आपकी मदद कर सकूंगा।

क्या आप चाहेंगे कि मैं इनमें से कोई मूल्यांकन करूं? बस "हां" या "चलिए" कहें।"""

            elif current_lang == "ta":
                return """**பரிந்துரை**: உங்கள் தற்போதைய நல்வாழ்வைப் புரிந்து கொள்ள உதவும் சில மனநல பரிசோதனைகள் இங்கே:

• **மனச்சோர்வு (PHQ-9)**: மனநிலை மற்றும் ஆர்வத்தின் அளவுகளை மதிப்பிடுதல்
• **கவலை (GAD-7)**: கவலை மற்றும் பதற்றத்தின் அளவுகளை மதிப்பிடுதல்

எந்தவொரு மதிப்பீட்டையும் முடித்த பிறகு, உங்கள் முடிவுகளைப் புரிந்து கொள்ளவும் அவை என்ன அர்த்தம் என்பதையும் நான் உங்களுக்கு உதவ முடியும்.

இந்த மதிப்பீடுகளில் ஏதேனும் ஒன்றை நான் செய்ய வேண்டுமா? "ஆம்" அல்லது "செய்வோம்" என்று சொல்லுங்கள்."""

            else:  # English
                return """**Quick Suggestion**: Here are some mental health screenings that might help you understand your current well-being:

• **Depression (PHQ-9)**: Assesses mood and interest levels
• **Anxiety (GAD-7)**: Evaluates anxiety and worry levels

After completing either assessment, I can help you understand your results and what they might mean.

Would you like me to walk you through this assessment? Just say "yes", "sure", or "let's do it"."""

    def _recently_suggested(self, suggestion_type: str, session: UserSession) -> bool:
        """Check if we suggested this type recently."""
        # Simple implementation - could be enhanced with session tracking
        return False  # For now, always allow suggestions

    def _update_suggestion_history(self, suggestion_type: str, session: UserSession):
        """Update suggestion history."""
        # Could store in session context for tracking
        pass

    def _should_suggest_mood_summary(self, user_msg: str, bot_response: str, session: UserSession) -> bool:
        """Determine if we should suggest mood summary (multilingual)."""
        if self._recently_suggested('mood', session):
            return False

        # Suggest if user asks about patterns, progress, or tracking (multilingual)
        mood_summary_patterns = [
            # English
            r'\b(how.*been.*feeling|pattern|progress|track|over time)\b',
            r'\b(getting better|getting worse|changing|improving)\b',
            r'\b(last week|past few days|recently|lately)\b',
            # Hindi
            r'\b(कैसा.*महसूस.*कर रहा|पैटर्न|प्रगति|ट्रैक|समय के साथ)\b',
            r'\b(बेहतर हो रहा|बदतर हो रहा|बदल रहा|सुधार)\b',
            r'\b(पिछले हफ्ते|पिछले कुछ दिन|हाल ही में)\b',
            # Tamil
            r'\b(எப்படி.*உணர்.*கிறீர்கள்|வடிவम்|முன्नேत्रम्|கண்காणிப्पु|समय के साथ)\b',
            r'\b(बेहतर.*आ रहा|खराब.*हो रहा|மாत्रम्|सुधार)\b',
            r'\b(கடந्த वारम्|கடந्த कुछ दिन|हाल ही में)\b'
        ]

        user_lower = user_msg.lower()
        has_mood_data = session and len(session.database.get_mood_summary(session.user_id)) > 0

        return has_mood_data and any(re.search(pattern, user_lower) for pattern in mood_summary_patterns)

    def _should_suggest_result_analysis(self, user_msg: str, bot_response: str, session: UserSession) -> bool:
        """Determine if we should suggest result analysis (multilingual)."""
        if self._recently_suggested('results', session):
            return False

        # Check if user is sharing actual scores but didn't get analyzed
        score_patterns = [
            # English
            r'\b(score.*\d+|got.*\d+|result.*\d+|\d+.*score)\b',
            r'\b(took.*test|completed.*assessment|got.*results|external)\b',
            # Hindi
            r'\b(स्कोर.*\d+|मिला.*\d+|परिणाम.*\d+|\d+.*स्कोर)\b',
            r'\b(टेस्ट लिया|मूल्यांकन पूरा|परिणाम मिले|बाहरी)\b',
            # Tamil
            r'\b(मतिप्पेण्.*\d+|मिळाले.*\d+|पরिणाम.*\d+|\d+.*मतिप्पेण्)\b',
            r'\b(परीक्षा.*एलुत्तु|मूल्यांकन.*मुदित्तु|पরিणाम.*वांदु|वेळियूर)\b'
        ]

        user_lower = user_msg.lower()
        return any(re.search(pattern, user_lower) for pattern in score_patterns)

    def _get_mood_summary_suggestion_multilingual(self, session: UserSession) -> str:
        """Generate mood summary suggestion (multilingual)."""
        mood_data = session.database.get_mood_summary(session.user_id) if session else {}
        current_lang = self.language_manager.current_language.value

        if mood_data:
            if current_lang == "hi":
                summary_text = "**आपके हाल के मूड पैटर्न**:\n"
                for date, moods in mood_data.items():
                    mood_list = [m['mood'] for m in moods]
                    summary_text += f"• {date}: {', '.join(mood_list)}\n"
                summary_text += "\nमैं देख रहा हूं कि आप अपने मूड पैटर्न के बारे में पूछ रहे हैं। यह वही है जो मैंने हमारी बातचीत के दौरान देखा है।"
                return summary_text

            elif current_lang == "ta":
                summary_text = "**உங்கள் சமீபத்திய மனநிலை வடிவங்கள்**:\n"
                for date, moods in mood_data.items():
                    mood_list = [m['mood'] for m in moods]
                    summary_text += f"• {date}: {', '.join(mood_list)}\n"
                summary_text += "\nநீங்கள் உங்கள் மனநிலை வடிவங்களைப் பற்றி கேட்கிறீர்கள் என்பதை நான் கவனிக்கிறேன். எங்கள் உரையாடல்களின் போது நான் கவனித்தது இதுதான்।"
                return summary_text

            else:  # English
                summary_text = "**Your Recent Mood Patterns**:\n"
                for date, moods in mood_data.items():
                    mood_list = [m['mood'] for m in moods]
                    summary_text += f"• {date}: {', '.join(mood_list)}\n"
                summary_text += "\nI notice you're asking about your mood patterns. This is what I've observed during our conversations."
                return summary_text
        else:
            if current_lang == "hi":
                return "**मूड ट्रैकिंग**: मैंने अभी तक पर्याप्त मूड डेटा ट्रैक नहीं किया है, लेकिन मैं समय के साथ पैटर्न की पहचान करने में मदद के लिए हमारी बातचीत के दौरान आप कैसा महसूस कर रहे हैं, इस पर ध्यान दे रहा हूं।"
            elif current_lang == "ta":
                return "**மனநிலை கண்காணிப்பு**: நான் இன்னும் போதுமான மனநிலை தரவைக் கண்காணிக்கவில்லை, ஆனால் காலப்போக்கில் வடிவங்களை அடையாளம் காண உதவ, எங்கள் உரையாடல்களின் போது நீங்கள் எப்படி உணர்கிறீர்கள் என்பதில் கவனம் செலுத்துகிறேன்."
            else:  # English
                return "**Mood Tracking**: I haven't tracked enough mood data yet, but I'm paying attention to how you're feeling during our conversations to help identify patterns over time."

    def _get_result_analysis_suggestion_multilingual(self) -> str:
        """Generate result analysis suggestion (multilingual)."""
        current_lang = self.language_manager.current_language.value

        if current_lang == "hi":
            return """**मूल्यांकन विश्लेषण**: मैं उन मूल्यांकन परिणामों को समझने में आपकी मदद करने में खुश हूं! आप अपने स्कोर मुझसे इस तरह साझा कर सकते हैं:

"मुझे PHQ-9 पर 12 स्कोर मिला" या "मेरा GAD-7 परिणाम 8 था"

मैं तब समझा सकूंगा कि इन संख्याओं का क्या मतलब है और आपकी मानसिक स्वास्थ्य जांच के बारे में व्यक्तिगत अंतर्दृष्टि प्रदान कर सकूंगा।"""

        elif current_lang == "ta":
            return """**மதிப்பீடு பகுப்பாய்வு**: அந்த மதிப்பீடு முடிவுகளைப் புரிந்து கொள்ள உங்களுக்கு உதவ நான் மகிழ்ச்சியாக இருக்கிறேன்! நீங்கள் உங்கள் மதிப்பெண்களை என்னுடன் இப்படி பகிர்ந்து கொள்ளலாம்:

"எனக்கு PHQ-9 இல் 12 மதிப்பெண் கிடைத்தது" அல்லது "என் GAD-7 முடிவு 8 ஆக இருந்தது"

பின்னர் இந்த எண்களின் அர்த்தம் என்ன என்பதை விளக்கி, உங்கள் மனநல பரிசோதனையைப் பற்றிய தனிப்பட்ட நுண்ணறிவுகளை வழங்க முடியும்।"""

        else:  # English
            return """**Assessment Analysis**: I'd be happy to help you understand those assessment results! You can share your scores with me like this:

"I got a score of 12 on the PHQ-9" or "My GAD-7 result was 8"

I can then explain what these numbers mean and provide personalized insights about your mental health screening."""

    def _detect_and_analyze_scores(self, user_message: str) -> Optional[str]:
        """Detect if user is sharing assessment scores and analyze them (multilingual)."""
        user_lower = user_message.lower()

        # Look for PHQ-9 scores (multilingual patterns)
        phq_patterns = [
            # English
            r'\b(?:phq.*?(\d+)|(\d+).*?phq)\b',
            r'\b(?:depression.*?score.*?(\d+)|(\d+).*?depression.*?score)\b',
            # Hindi
            r'\b(?:अवसाद.*?स्कोर.*?(\d+)|(\d+).*?अवसाद.*?स्कोर)\b',
            r'\b(?:phq.*?(\d+)|(\d+).*?phq)\b',
            # Tamil
            r'\b(?:மனச्चோর्वु.*?मतिप्पेण्.*?(\d+)|(\d+).*?মনચ्চোর्वु.*?मतिप्पेण्)\b',
            r'\b(?:phq.*?(\d+)|(\d+).*?phq)\b'
        ]

        # Look for GAD-7 scores (multilingual patterns)
        gad_patterns = [
            # English
            r'\b(?:gad.*?(\d+)|(\d+).*?gad)\b',
            r'\b(?:anxiety.*?score.*?(\d+)|(\d+).*?anxiety.*?score)\b',
            # Hindi
            r'\b(?:चिंता.*?स्कोर.*?(\d+)|(\d+).*?चिंता.*?स्कोर)\b',
            r'\b(?:gad.*?(\d+)|(\d+).*?gad)\b',
            # Tamil
            r'\b(?:কवলै.*?मतিप्पेण্.*?(\d+)|(\d+).*?কवলै.*?मतिप्पেण্)\b',
            r'\b(?:gad.*?(\d+)|(\d+).*?gad)\b'
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

        # General score patterns with context clues
        general_patterns = [
            r'\b(?:score.*?(\d+)|got.*?(\d+)|result.*?(\d+)|मिला.*?(\d+)|स्कोर.*?(\d+)|परिणाम.*?(\d+))\b'
        ]

        for pattern in general_patterns:
            match = re.search(pattern, user_lower)
            if match:
                score = int([g for g in match.groups() if g][0])

                # Determine type based on context
                if any(word in user_lower for word in ['depression', 'sad', 'down', 'phq', 'अवसाद', 'उदास', 'मनच्चोর्वु']):
                    if 0 <= score <= 27:
                        return self.analyze_assessment_results('phq9', score)
                elif any(word in user_lower for word in ['anxiety', 'anxious', 'worried', 'gad', 'चिंता', 'घबराया', 'कवलै']):
                    if 0 <= score <= 21:
                        return self.analyze_assessment_results('gad7', score)

        return None

    def change_language(self, new_language: SupportedLanguage, session: UserSession = None) -> str:
        """Change the current language and save preference."""
        self.language_manager.set_language(new_language)

        if session and session.user_id:
            self.language_manager.save_user_language_preference(session.user_id, new_language)

        return self.language_manager.get_text('language_changed')

    def get_localized_text(self, key: str, **kwargs) -> str:
        """Get localized text for current language."""
        return self.language_manager.get_text(key, **kwargs)