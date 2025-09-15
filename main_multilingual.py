#!/usr/bin/env python3
"""
MindMate Mental Health Chatbot - Multilingual CLI Interface
Supports English, Hindi, and Tamil with cultural sensitivity
Usage: python main_multilingual.py [--backend] [--user-id USER_ID] [--language LANG]
"""

import os
import time
import re
import argparse
from dotenv import load_dotenv
from multilingual_chatbot import MultilingualMindMateChatbot
from language_manager import SupportedLanguage
from assessment_api import AssessmentAPIClient, MockAssessmentSession
from session_manager import get_user_id_from_env

def validate_input(user_input: str) -> tuple[bool, str]:
    """Validate if input is appropriate for mental health conversation."""
    # Patterns for multiple languages
    inappropriate_patterns = [
        # English
        r'\b(spam|advertisement|selling|buy now)\b',
        r'\b(explicit sexual|pornographic)\b',
        r'\b(illegal drugs|drug dealing)\b',
        r'\b(violence against others|harm others)\b',
        # Hindi
        r'\b(स्पैम|विज्ञापन|बेचना|खरीदना)\b',
        r'\b(अश्लील|पोर्नोग्राफिक)\b',
        # Tamil
        r'\b(ஸ்பேம்|விளம்பரம்|விற்பனை)\b',
        r'\b(ஆபாசம்|பார்னோகிராஃபிக்)\b'
    ]

    input_lower = user_input.lower()
    for pattern in inappropriate_patterns:
        if re.search(pattern, input_lower):
            return False, "inappropriate_content"

    return True, ""

def show_typing_indicator(chatbot):
    """Show localized typing indicator."""
    typing_text = chatbot.get_localized_text('typing_indicator')
    print(f"\n{typing_text}", end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()

def suggest_booking(chatbot):
    """Suggest counselor booking with localized resources."""
    resources = chatbot.language_manager.get_mental_health_resources()

    # Build localized booking suggestion
    current_lang = chatbot.language_manager.current_language.value

    if current_lang == "hi":
        suggestion = """
**पेशेवर सहायता उपलब्ध है**
किसी पेशेवर परामर्शदाता से बात करना आपके लिए वास्तव में सहायक हो सकता है।

क्या आप चाहेंगे कि मैं आपकी मदद करूं:
• स्थानीय मानसिक स्वास्थ्य पेशेवरों को खोजने में
• परामर्श सत्र बुक करने में
• विभिन्न प्रकार की चिकित्सा के बारे में जानने में

*अस्वीकरण: पेशेवर थेरेपी व्यक्तिगत सहायता प्रदान कर सकती है जो मैं AI सहायक के रूप में प्रदान कर सकता हूं उससे कहीं अधिक है।*

क्या आप परामर्शदाता से जुड़ने में सहायता चाहेंगे?"""

    elif current_lang == "ta":
        suggestion = """
**தொழில்முறை ஆதரவு கிடைக்கிறது**
ஒரு தொழில்முறை ஆலோசகருடன் பேசுவது உங்களுக்கு மிகவும் உதவிகரமாக இருக்கும்.

நான் உங்களுக்கு உதவ வேண்டுமா:
• உள்ளூர் மனநல நிபுணர்களைக் கண்டறிய
• ஆலோசனை அமர்வை முன்பதிவு செய்ய
• பல்வேறு வகையான சிகிச்சைகளைப் பற்றி அறிய

*மறுப்பு: தொழில்முறை சிகிச்சை தனிப்பட்ட ஆதரவை வழங்க முடியும், இது AI உதவியாளராக நான் வழங்கக்கூடியதை விட அதிகம்.*

ஆலோசகருடன் இணைக்க உதவி வேண்டுமா?"""

    else:  # English
        suggestion = """
**Professional Support Available**
It sounds like talking with a professional counselor could be really helpful for you.

Would you like me to help you:
• Find local mental health professionals
• Book a counseling session
• Learn about different types of therapy

*Disclaimer: Professional therapy can provide personalized support that goes beyond what I can offer as an AI assistant.*

Would you like assistance connecting with a counselor?"""

    return suggestion

def share_resources(chatbot, topic: str = "general"):
    """Share localized resources based on topic and language."""
    current_lang = chatbot.language_manager.current_language.value

    if current_lang == "hi":
        resources = {
            "anxiety": """
**चिंता प्रबंधन संसाधन**

**तत्काल तकनीकें:**
• 4-7-8 सांस: 4 गिनती में सांस लें, 7 रोकें, 8 में छोड़ें
• ग्राउंडिंग (5-4-3-2-1): 5 चीजें देखें, 4 छुएं, 3 सुनें, 2 सूंघें, 1 चखें
• प्रगतिशील मांसपेशी शिथिलता

**सहायक ऐप्स:**
• Headspace (ध्यान)
• Calm (नींद और आराम)
• स्थानीय योग और ध्यान ऐप्स

**और जानें:**
• स्थानीय मानसिक स्वास्थ्य केंद्र
• CBT तकनीकों पर स्व-सहायता पुस्तकें""",

            "depression": """
**अवसाद सहायता संसाधन**

**दैनिक रणनीतियां:**
• व्यवहारिक सक्रियता: दैनिक एक छोटी सार्थक गतिविधि
• प्रकाश संपर्क: 10-15 मिनट धूप में बैठना
• कोमल आंदोलन: छोटी सैर या स्ट्रेचिंग
• सामाजिक संपर्क: किसी एक व्यक्ति से संपर्क करें

**सहायक उपकरण:**
• मूड ट्रैकिंग ऐप्स
• कृतज्ञता डायरी
• संरचित दैनिक दिनचर्या

**पेशेवर संसाधन:**
• स्थानीय मानसिक स्वास्थ्य केंद्र
• सरकारी स्वास्थ्य योजनाएं""",

            "general": """
**मानसिक स्वास्थ्य संसाधन**

**संकट सहायता:**
• राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन: 112
• मानसिक स्वास्थ्य हेल्पलाइन: 9152987821
• SAMHSA हेल्पलाइन: 1-800-662-4357

**स्व-देखभाल उपकरण:**
• माइंडफुलनेस और ध्यान ऐप्स
• पत्रिका लेखन संकेत
• सांस की एक्सरसाइज
• नियमित नींद कार्यक्रम

**पेशेवर सहायता:**
• स्थानीय चिकित्सक खोजें
• सामुदायिक मानसिक स्वास्थ्य केंद्र
• कर्मचारी सहायता कार्यक्रम"""
        }

    elif current_lang == "ta":
        resources = {
            "anxiety": """
**கவலை மேலாண்மை ஆதாரங்கள்**

**உடனடி நுட்பங்கள்:**
• 4-7-8 மூச்சு: 4 எண்ணிக்கையில் உள்ளே, 7 பிடித்து, 8 இல் வெளியே
• மனதை அமைதிப்படுத்துதல் (5-4-3-2-1): 5 பார்க்கவும், 4 தொடவும், 3 கேட்கவும், 2 நுகரவும், 1 சுவைக்கவும்
• படிப்படியாக தசை தளர்வு

**உதவிகரமான ஆப்ஸ்:**
• Headspace (தியானம்)
• Calm (உறக்கம் & ஓய்வு)
• உள்ளூர் யோகா மற்றும் தியான ஆப்ஸ்

**மேலும் அறிய:**
• உள்ளூர் மனநல மையங்கள்
• CBT நுட்பங்களில் சுய உதவி புத்தகங்கள்""",

            "depression": """
**மனச்சோர்வு ஆதரவு ஆதாரங்கள்**

**தினசரி உத்திகள்:**
• நடத்தை செயல்பாடு: தினமும் ஒரு சிறிய அர்த்தமுள்ள செயல்பாடு
• ஒளி வெளிப்பாடு: 10-15 நிமிடங்கள் சூரிய ஒளி
• மென்மையான இயக்கம்: குறுகிய நடைபயிற்சி அல்லது நீட்டி
• சமூக தொடர்பு: ஒரு நபரை அணுகுங்கள்

**உதவிகரமான கருவிகள்:**
• மனநிலை கண்காணிப்பு ஆப்ஸ்
• நன்றியுணர்வு நாட்குறிப்பு
• கட்டமைக்கப்பட்ட தினசரி வழக்கம்

**தொழில்முறை ஆதாரங்கள்:**
• உள்ளூர் மனநல மையங்கள்
• அரசு சுகாதார திட்டங்கள்""",

            "general": """
**மனநல ஆதாரங்கள்**

**நெருக்கடி ஆதரவு:**
• தேசிய தற்கொலை தடுப்பு ஹெல்ப்லைன்: 108
• மனநல ஹெல்ப்லைன்: 9152987821
• SAMHSA ஹெல்ப்லைன்: 1-800-662-4357

**சுய பராமரிப்பு கருவிகள்:**
• நினைவாற்றல் மற்றும் தியான ஆப்ஸ்
• பத்திரிகை எழுதும் தூண்டுதல்கள்
• மூச்சு பயிற்சிகள்
• வழக்கமான தூக்க அட்டவணை

**தொழில்முறை உதவி:**
• உள்ளூர் சிகிச்சையாளர்களைக் கண்டறியவும்
• சமூக மனநல மையங்கள்
• பணியாளர் உதவி திட்டங்கள்"""
        }

    else:  # English
        resources = {
            "anxiety": """
**Anxiety Management Resources**

**Immediate Techniques:**
• 4-7-8 Breathing: Inhale 4, hold 7, exhale 8
• 5-4-3-2-1 Grounding: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste
• Progressive muscle relaxation

**Helpful Apps:**
• Headspace (meditation)
• Calm (sleep & relaxation)
• DARE (anxiety management)

**Learn More:**
• Anxiety and Depression Association (adaa.org)
• Self-help workbooks on CBT techniques""",

            "depression": """
**Depression Support Resources**

**Daily Strategies:**
• Behavioral activation: One small meaningful activity daily
• Light exposure: 10-15 minutes of sunlight
• Gentle movement: Short walks or stretching
• Social connection: Reach out to one person

**Helpful Tools:**
• Mood tracking apps
• Gratitude journaling
• Structured daily routine

**Professional Resources:**
• National Alliance on Mental Illness (nami.org)
• Depression and Bipolar Support Alliance (dbsalliance.org)""",

            "general": """
**Mental Health Resources**

**Crisis Support:**
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• SAMHSA Helpline: 1-800-662-4357

**Self-Care Tools:**
• Mindfulness and meditation apps
• Journaling prompts
• Breathing exercises
• Regular sleep schedule

**Professional Help:**
• Psychology Today (therapist finder)
• Local community mental health centers
• Employee assistance programs"""
        }

    return resources.get(topic, resources["general"])

def analyze_triggers(message: str) -> str:
    """Analyze message for booking and resource triggers in multiple languages."""
    message_lower = message.lower()

    # Booking triggers (multiple languages)
    booking_patterns = [
        # English
        r'\b(need help|want therapy|see therapist|professional help|counselor)\b',
        # Hindi
        r'\b(मदद चाहिए|थेरेपी चाहिए|डॉक्टर मिलना|पेशेवर मदद|परामर्शदाता)\b',
        # Tamil
        r'\b(உதவி வேண்டும்|சிகிச்சை வேண்டும்|டாக்டர் பார்க்க|தொழில்முறை உதவி|ஆலோசகர்)\b'
    ]

    for pattern in booking_patterns:
        if re.search(pattern, message_lower):
            return "booking"

    # Resource triggers (multiple languages)
    resource_patterns = [
        # English
        r'\b(coping|techniques|exercises|tools|strategies|tips)\b',
        # Hindi
        r'\b(निपटना|तकनीकें|अभ्यास|उपकरण|रणनीतियां|सुझाव)\b',
        # Tamil
        r'\b(சமாளித்தல்|நுட்பங்கள்|பயிற்சிகள்|கருவிகள்|உத்திகள்|குறிப்புகள்)\b'
    ]

    for pattern in resource_patterns:
        if re.search(pattern, message_lower):
            mood = "anxiety" if any(word in message_lower for word in ["anx", "चिंता", "கவலை"]) else \
                   "depression" if any(word in message_lower for word in ["depress", "अवसाद", "மனச்சோர்வு"]) else \
                   "general"
            return f"resources_{mood}"

    return "none"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MindMate Multilingual Mental Health Chatbot")
    parser.add_argument("--backend", action="store_true",
                       help="Use backend API instead of local storage")
    parser.add_argument("--user-id", type=str,
                       help="Specify user ID (optional)")
    parser.add_argument("--language", type=str, choices=["en", "hi", "ta"],
                       help="Set language (en=English, hi=Hindi, ta=Tamil)")
    parser.add_argument("--api-url", type=str,
                       help="Backend API URL (if using backend)")
    parser.add_argument("--api-key", type=str,
                       help="Backend API key (if using backend)")
    return parser.parse_args()

def main():
    load_dotenv()
    args = parse_arguments()

    # Get OpenAI API key from environment
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("ERROR: Please set OPENAI_API_KEY in your .env file")
        print("त्रुटि: कृपया अपनी .env फ़ाइल में OPENAI_API_KEY सेट करें")
        print("பிழை: தயவுசெய்து உங்கள் .env கோப்பில் OPENAI_API_KEY ஐ அமைக்கவும்")
        return

    # Get or generate user ID
    user_id = args.user_id or get_user_id_from_env()

    # Initialize multilingual chatbot
    db_kwargs = {}
    if args.backend:
        if args.api_url:
            db_kwargs['api_base_url'] = args.api_url
        if args.api_key:
            db_kwargs['api_key'] = args.api_key

    chatbot = MultilingualMindMateChatbot(openai_api_key, use_backend=args.backend, **db_kwargs)

    # Set language if specified
    initial_language = None
    if args.language:
        lang_map = {"en": SupportedLanguage.ENGLISH, "hi": SupportedLanguage.HINDI, "ta": SupportedLanguage.TAMIL}
        initial_language = lang_map.get(args.language)

    # Start user session with language preference
    session = chatbot.start_session(user_id, initial_language)

    # Initialize assessment components
    assessment_client = AssessmentAPIClient()
    current_assessment = None

    # Welcome message - check if returning user
    if session.is_returning_user():
        welcome_msg = chatbot.get_localized_text('welcome_back')
    else:
        welcome_msg = chatbot.get_localized_text('welcome_message')

    print(welcome_msg)
    print(chatbot.get_localized_text('help_quit'))
    print("=" * 60)

    while True:
        try:
            user_input = input(f"\n{chatbot.language_manager.get_language_display_name()}: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye', 'बाहर', 'निकास', 'வெளியேறு', 'நிறுத்து']:
                print(f"\n{chatbot.get_localized_text('goodbye')}")
                break
            elif user_input.lower() in ['help', 'मदद', 'உதவி']:
                print(f"\n{chatbot.get_localized_text('help_title')}")
                print(f"• {chatbot.get_localized_text('help_clear')}")
                print(f"• {chatbot.get_localized_text('help_mood')}")
                print(f"• {chatbot.get_localized_text('help_assessment')}")
                print(f"• {chatbot.get_localized_text('help_results')}")
                print(f"• {chatbot.get_localized_text('help_session')}")
                print(f"• {chatbot.get_localized_text('help_language')}")
                print(f"• {chatbot.get_localized_text('help_quit')}")
                continue
            elif user_input.lower() in ['clear', 'साफ', 'அழிக்கு']:
                # Start new session
                session = chatbot.start_session(user_id, chatbot.language_manager.current_language)
                print(f"\n{chatbot.get_localized_text('conversation_cleared')}")
                continue
            elif user_input.lower() in ['mood', 'मूड', 'மனநிலை']:
                mood_data = chatbot.get_mood_summary(session)
                if mood_data:
                    print(f"\n{chatbot.get_localized_text('mood_summary_title')}")
                    for date, moods in mood_data.items():
                        print(f"  {date}: {[m['mood'] for m in moods]}")
                else:
                    print(f"\n{chatbot.get_localized_text('no_mood_data')}")
                continue
            elif user_input.lower() in ['session', 'सत्र', 'அமர்வு']:
                session_info = chatbot.get_session_info()
                print(f"\n{chatbot.get_localized_text('session_info_title')}")
                print(chatbot.get_localized_text('session_user_id', user_id=session_info.get('user_id', 'Unknown')))
                print(chatbot.get_localized_text('session_duration', duration=session_info.get('session_duration_minutes', 0)))
                print(chatbot.get_localized_text('session_returning', returning=session_info.get('is_returning_user', False)))
                print(chatbot.get_localized_text('session_conversations', count=session_info.get('user_profile', {}).get('conversation_count', 0)))
                continue
            elif user_input.lower() in ['language', 'भाषा', 'மொழி']:
                new_language = chatbot.language_manager.show_language_selection()
                change_msg = chatbot.change_language(new_language, session)
                print(f"\n{change_msg}")
                continue
            # Natural language assessment triggers
            elif any(re.search(pattern, user_input.lower()) for pattern in [
                # English direct request patterns
                r'\b(test me|assess me|check me|evaluate me|screening|mental health check)\b',
                # Hindi direct request patterns
                r'\b(मेरी जांच करें|मेरा मूल्यांकन करें|मुझे जांचें|मानसिक स्वास्थ्य जांच)\b',
                # Tamil direct request patterns
                r'\b(என்னை பரிசோதி|என்னை மதிப்பீடு|மனநல பரிசோதனை|என்னை சோதி)\b'
            ]):
                print(f"\n{chatbot.get_localized_text('assessment_title')}")
                print(chatbot.get_localized_text('assessment_question'))
                print(chatbot.get_localized_text('assessment_phq9'))
                print(chatbot.get_localized_text('assessment_gad7'))
                print(chatbot.get_localized_text('assessment_external'))

                assessment_choice = input(f"{chatbot.get_localized_text('assessment_choice_prompt')}").strip()

                if assessment_choice == "1":
                    current_assessment = MockAssessmentSession('phq9')
                    print(f"\n{chatbot.get_localized_text('phq9_title')}")
                    print(chatbot.get_localized_text('assessment_disclaimer'))
                    print(chatbot.get_localized_text('assessment_instructions', count=9))
                    print(chatbot.get_localized_text('assessment_scale_0'))
                    print(chatbot.get_localized_text('assessment_scale_1'))
                    print(chatbot.get_localized_text('assessment_scale_2'))
                    print(chatbot.get_localized_text('assessment_scale_3'))

                    # Get localized questions
                    questions = chatbot.language_manager.get_assessment_questions('phq9')
                    if questions:
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=questions[0]))
                    else:
                        question = current_assessment.get_current_question()
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=question['text']))
            elif user_input.lower() in ['assessment', 'मूल्यांकन', 'மதிப்பீடு']:
                print(f"\n{chatbot.get_localized_text('assessment_title')}")
                print(chatbot.get_localized_text('assessment_question'))
                print(chatbot.get_localized_text('assessment_phq9'))
                print(chatbot.get_localized_text('assessment_gad7'))
                print(chatbot.get_localized_text('assessment_external'))

                assessment_choice = input(f"{chatbot.get_localized_text('assessment_choice_prompt')}").strip()

                if assessment_choice == "1":
                    current_assessment = MockAssessmentSession('phq9')
                    print(f"\n{chatbot.get_localized_text('phq9_title')}")
                    print(chatbot.get_localized_text('assessment_disclaimer'))
                    print(chatbot.get_localized_text('assessment_instructions', count=9))
                    print(chatbot.get_localized_text('assessment_scale_0'))
                    print(chatbot.get_localized_text('assessment_scale_1'))
                    print(chatbot.get_localized_text('assessment_scale_2'))
                    print(chatbot.get_localized_text('assessment_scale_3'))

                    # Get localized questions
                    questions = chatbot.language_manager.get_assessment_questions('phq9')
                    if questions:
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=questions[0]))
                    else:
                        question = current_assessment.get_current_question()
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=question['text']))

                elif assessment_choice == "2":
                    current_assessment = MockAssessmentSession('gad7')
                    print(f"\n{chatbot.get_localized_text('gad7_title')}")
                    print(chatbot.get_localized_text('assessment_disclaimer'))
                    print(chatbot.get_localized_text('assessment_instructions', count=7))
                    print(chatbot.get_localized_text('assessment_scale_0'))
                    print(chatbot.get_localized_text('assessment_scale_1'))
                    print(chatbot.get_localized_text('assessment_scale_2'))
                    print(chatbot.get_localized_text('assessment_scale_3'))

                    # Get localized questions
                    questions = chatbot.language_manager.get_assessment_questions('gad7')
                    if questions:
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=questions[0]))
                    else:
                        question = current_assessment.get_current_question()
                        print(chatbot.get_localized_text('assessment_question_num', num=1, text=question['text']))

                elif assessment_choice == "3":
                    print(f"\n{chatbot.get_localized_text('external_assessment_title')}")
                    print(chatbot.get_localized_text('external_phq9', link=assessment_client.get_assessment_link('phq9')))
                    print(chatbot.get_localized_text('external_gad7', link=assessment_client.get_assessment_link('gad7')))
                    print(chatbot.get_localized_text('external_instructions'))
                else:
                    print(chatbot.get_localized_text('assessment_invalid'))
                continue
            elif user_input.lower() in ['results', 'परिणाम', 'முடிவுகள்']:
                print(f"\n{chatbot.get_localized_text('results_title')}")
                print(chatbot.get_localized_text('results_instructions'))

                assessment_type = input(chatbot.get_localized_text('results_type_prompt')).strip().lower()
                if assessment_type not in ['phq9', 'gad7']:
                    print(chatbot.get_localized_text('results_invalid_type'))
                    continue

                try:
                    total_score = int(input(chatbot.get_localized_text('results_score_prompt')).strip())
                    responses_input = input(chatbot.get_localized_text('results_responses_prompt')).strip()

                    responses = None
                    if responses_input:
                        responses = [int(r.strip()) for r in responses_input.split(',')]

                    # Get multilingual chatbot analysis
                    analysis = chatbot.analyze_assessment_results(assessment_type, total_score, responses, session)
                    print(f"\nMindMate: {analysis}")

                except ValueError:
                    print(chatbot.get_localized_text('results_invalid_input'))
                continue
            elif not user_input:
                continue

            # Check for direct assessment requests first
            assessment_request_patterns = [
                # English - Direct requests
                r'\b(test me|check me|assess me|evaluate me|screen me)\b',
                r'\b(I want.*test|I need.*assessment|can you check|please evaluate)\b',
                r'\b(depression test|anxiety test|mental health check)\b',
                # Hindi - Direct requests
                r'\b(मेरी जांच करें|मेरा टेस्ट करें|मूल्यांकन करें|जांच लें)\b',
                r'\b(मुझे.*टेस्ट|मुझे.*जांच|कृपया जांच|कृपया देखें)\b',
                r'\b(अवसाद टेस्ट|चिंता टेस्ट|मानसिक स्वास्थ्य जांच)\b',
                # Tamil - Direct requests
                r'\b(என்னை பরிசோதி|என்னை சோதி|மதிப்பீடு செய்|சோதனை செய்)\b',
                r'\b(எனக்கு.*சோதனை|எனக்கு.*பরிசோதனை|தயவுসெய়து পার්|தயವুসെய்து সோথি)\b',
                r'\b(மனச्চোர्वு சোதনை|கவলै சோதனை|मनநল পরীক্षা)\b'
            ]

            user_lower = user_input.lower()

            # Check if user directly requested an assessment
            if any(re.search(pattern, user_lower) for pattern in assessment_request_patterns):
                # Determine assessment type based on keywords
                if any(word in user_lower for word in ['depression', 'sad', 'down', 'अवसाद', 'उदास', 'மனच्चोর्वু']):
                    current_assessment = MockAssessmentSession('phq9')
                    print(f"\n{chatbot.get_localized_text('phq9_title')}")
                elif any(word in user_lower for word in ['anxiety', 'anxious', 'worry', 'चिंता', 'घबराहट', 'কवলै']):
                    current_assessment = MockAssessmentSession('gad7')
                    print(f"\n{chatbot.get_localized_text('gad7_title')}")
                else:
                    # Default to depression assessment
                    current_assessment = MockAssessmentSession('phq9')
                    print(f"\n{chatbot.get_localized_text('phq9_title')}")

                print(chatbot.get_localized_text('assessment_disclaimer'))
                question_count = 9 if current_assessment.assessment_type == 'phq9' else 7
                print(chatbot.get_localized_text('assessment_instructions', count=question_count))
                print(chatbot.get_localized_text('assessment_scale_0'))
                print(chatbot.get_localized_text('assessment_scale_1'))
                print(chatbot.get_localized_text('assessment_scale_2'))
                print(chatbot.get_localized_text('assessment_scale_3'))

                questions = chatbot.language_manager.get_assessment_questions(current_assessment.assessment_type)
                if questions:
                    print(chatbot.get_localized_text('assessment_question_num', num=1, text=questions[0]))
                else:
                    question = current_assessment.get_current_question()
                    print(chatbot.get_localized_text('assessment_question_num', num=1, text=question['text']))
                continue

            # Check for natural language assessment consent
            consent_patterns = [
                # English
                r'\b(yes|yeah|sure|okay|ok|go ahead|let\'s do it|sounds good)\b',
                # Hindi
                r'\b(हां|जी हां|ठीक है|चलिए|करते हैं|सही है)\b',
                # Tamil
                r'\b(ஆம்|சரி|ओके|वরुकिळें|सेळ्लाम्)\b'
            ]

            user_lower = user_input.lower()
            if any(re.search(pattern, user_lower) for pattern in consent_patterns):
                # User consented to assessment - use intelligent selection
                # Analyze recent conversation context to determine appropriate assessment
                recent_message = user_input.lower()

                # Check for mood indicators in recent context
                depression_score = sum(1 for word in [
                    'depression', 'depressed', 'sad', 'down', 'hopeless', 'empty', 'tired',
                    'अवसाद', 'उदास', 'निराश', 'खाली', 'थका', 'मनच्छोर्वु'
                ] if word in recent_message)

                anxiety_score = sum(1 for word in [
                    'anxiety', 'anxious', 'worry', 'nervous', 'panic', 'stress', 'overwhelmed',
                    'चिंता', 'घबराहट', 'तनाव', 'बेचैन', 'কवলै', 'পদর্রম্'
                ] if word in recent_message)

                # Select assessment type based on context
                if anxiety_score > depression_score:
                    current_assessment = MockAssessmentSession('gad7')
                    print(f"\n{chatbot.get_localized_text('gad7_title')}")
                else:
                    current_assessment = MockAssessmentSession('phq9')
                    print(f"\n{chatbot.get_localized_text('phq9_title')}")

                print(chatbot.get_localized_text('assessment_disclaimer'))
                question_count = 7 if current_assessment.assessment_type == 'gad7' else 9
                print(chatbot.get_localized_text('assessment_instructions', count=question_count))
                print(chatbot.get_localized_text('assessment_scale_0'))
                print(chatbot.get_localized_text('assessment_scale_1'))
                print(chatbot.get_localized_text('assessment_scale_2'))
                print(chatbot.get_localized_text('assessment_scale_3'))

                # Get localized questions
                questions = chatbot.language_manager.get_assessment_questions('phq9')
                if questions:
                    print(chatbot.get_localized_text('assessment_question_num', num=1, text=questions[0]))
                else:
                    question = current_assessment.get_current_question()
                    print(chatbot.get_localized_text('assessment_question_num', num=1, text=question['text']))
                continue

            # Handle active assessment
            if current_assessment and current_assessment.active:
                # Try to parse natural language responses first
                natural_response_num = None

                # Natural language patterns for assessment responses
                if any(re.search(pattern, user_lower) for pattern in [
                    # English - "Not at all" (0)
                    r'\b(not at all|never|no|none|zero)\b',
                    # Hindi - "बिल्कुल नहीं" (0)
                    r'\b(बिल्कुल नहीं|कभी नहीं|नहीं|कोई नहीं|शून्य)\b',
                    # Tamil - "கொஞ்சம் கூட இல்லை" (0)
                    r'\b(कोण्जम् कूद इल्लै|कभी इल्लै|इल्लै|ओन्रम् इल्लै)\b'
                ]):
                    natural_response_num = 0
                elif any(re.search(pattern, user_lower) for pattern in [
                    # English - "Several days" (1)
                    r'\b(several days|some days|a few days|sometimes|occasionally|little bit)\b',
                    # Hindi - "कुछ दिन" (1)
                    r'\b(कुछ दिन|कई दिन|कभी कभी|थोड़ा सा|कम)\b',
                    # Tamil - "சில நாட்கள்" (1)
                    r'\b(सिल नाट्कळ्|कोण्जम्|कमी|कभी कभी)\b'
                ]):
                    natural_response_num = 1
                elif any(re.search(pattern, user_lower) for pattern in [
                    # English - "More than half the days" (2)
                    r'\b(more than half|most days|often|frequently|usually|quite a bit)\b',
                    # Hindi - "आधे से अधिक दिन" (2)
                    r'\b(आधे से अधिक|ज्यादा दिन|अक्सर|बहुत बार|ज्यादातर)\b',
                    # Tamil - "பாதிக்கு மேற்பட்ட நாட்கள்" (2)
                    r'\b(पाদिक्कु मेर्पद्द|अदिकम्|अक्सर|अधिक नाट्कळ्)\b'
                ]):
                    natural_response_num = 2
                elif any(re.search(pattern, user_lower) for pattern in [
                    # English - "Nearly every day" (3)
                    r'\b(nearly every day|almost every day|every day|always|constantly|all the time)\b',
                    # Hindi - "लगभग हर दिन" (3)
                    r'\b(लगभग हर दिन|हर दिन|हमेशा|लगातार|पूरे समय|बहुत ज्यादा)\b',
                    # Tamil - "கிட்டத்தட்ட எல்லா நாட்களும்" (3)
                    r'\b(किट्टत्तट्ट एल्ला नाट्कळुम्|एल्ला नाळुम्|एप्पोळुम्|मिक अदिकम्)\b'
                ]):
                    natural_response_num = 3

                # Try numeric input if natural language didn't match
                if natural_response_num is None:
                    try:
                        response_num = int(user_input.strip())
                        if response_num not in [0, 1, 2, 3]:
                            print(chatbot.get_localized_text('assessment_invalid_response'))
                            continue
                    except ValueError:
                        print(chatbot.get_localized_text('assessment_invalid_response'))
                        continue
                else:
                    response_num = natural_response_num

                # Submit response
                if current_assessment.submit_response(response_num):
                    if current_assessment.is_complete():
                        # Assessment complete - get results and analyze
                        results = current_assessment.get_results()
                        print(f"\n{chatbot.get_localized_text('assessment_completed')}")

                        # Get multilingual chatbot analysis
                        analysis = chatbot.analyze_assessment_results(
                            current_assessment.assessment_type,
                            results['total_score'],
                            results['responses'],
                            session
                        )
                        print(f"\nMindMate: {analysis}")

                        # Reset assessment
                        current_assessment = None
                    else:
                        # Ask next question
                        question_num = current_assessment.current_question + 1

                        # Get localized questions
                        questions = chatbot.language_manager.get_assessment_questions(current_assessment.assessment_type)
                        if questions and question_num <= len(questions):
                            question_text = questions[question_num - 1]
                        else:
                            question = current_assessment.get_current_question()
                            question_text = question['text']

                        print(chatbot.get_localized_text('assessment_question_num',
                                                       num=question_num, text=question_text))
                else:
                    print(chatbot.get_localized_text('assessment_invalid_response'))
                continue

            # Input validation
            is_valid, warning_key = validate_input(user_input)
            if not is_valid:
                warning_msg = chatbot.get_localized_text('content_warning')
                print(f"\nMindMate: {warning_msg}")
                continue

            # Show typing indicator
            show_typing_indicator(chatbot)

            try:
                # Get multilingual chatbot response
                response = chatbot.chat(user_input, session)
                print(f"MindMate: {response}")

                # Check for additional triggers (booking and resources)
                if not current_assessment:
                    trigger = analyze_triggers(user_input)

                    if trigger == "booking":
                        print(suggest_booking(chatbot))
                    elif trigger.startswith("resources_"):
                        resource_type = trigger.split("_")[1]
                        print(share_resources(chatbot, resource_type))

            except Exception as api_error:
                error_msg = chatbot.get_localized_text('api_error')
                crisis_msg = chatbot.get_localized_text('crisis_backup')
                print(f"MindMate: {error_msg}")
                print(crisis_msg)

        except KeyboardInterrupt:
            print(f"\n\n{chatbot.get_localized_text('goodbye')}")
            break
        except Exception as e:
            error_msg = chatbot.get_localized_text('general_error')
            crisis_msg = chatbot.get_localized_text('crisis_backup')
            print(f"\n{error_msg}")
            print(crisis_msg)

if __name__ == "__main__":
    main()