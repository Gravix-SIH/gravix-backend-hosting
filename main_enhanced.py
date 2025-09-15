#!/usr/bin/env python3
"""
MindMate Mental Health Chatbot - Enhanced CLI Interface with Database Integration
Usage: python main_enhanced.py [--backend] [--user-id USER_ID]
"""

import os
import time
import re
import argparse
from dotenv import load_dotenv
from enhanced_chatbot import EnhancedMindMateChatbot
from assessment_api import AssessmentAPIClient, MockAssessmentSession
from session_manager import get_user_id_from_env

def validate_input(user_input: str) -> tuple[bool, str]:
    """Validate if input is appropriate for mental health conversation."""
    inappropriate_patterns = [
        r'\b(spam|advertisement|selling|buy now)\b',
        r'\b(explicit sexual|pornographic)\b',
        r'\b(illegal drugs|drug dealing)\b',
        r'\b(violence against others|harm others)\b'
    ]

    input_lower = user_input.lower()
    for pattern in inappropriate_patterns:
        if re.search(pattern, input_lower):
            return False, "Please keep our conversation supportive and safe."

    return True, ""

def show_typing_indicator():
    """Show typing indicator."""
    print("\nMindMate is typing", end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()

def suggest_booking():
    """Suggest counselor booking."""
    return """
**Professional Support Available**
It sounds like talking with a professional counselor could be really helpful for you.

Would you like me to help you:
• Find local mental health professionals
• Book a counseling session
• Learn about different types of therapy

*Disclaimer: Professional therapy can provide personalized support that goes beyond what I can offer as an AI assistant.*

Would you like assistance connecting with a counselor?"""

def share_resources(topic: str = "general"):
    """Share structured resources based on topic."""
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
    """Analyze message for booking and resource triggers."""
    message_lower = message.lower()

    # Check for booking triggers
    if re.search(r'\b(need help|want therapy|see therapist|professional help|counselor)\b', message_lower):
        return "booking"

    # Check for resource triggers
    if re.search(r'\b(coping|techniques|exercises|tools|strategies|tips)\b', message_lower):
        mood = "anxiety" if "anx" in message_lower else "depression" if "depress" in message_lower else "general"
        return f"resources_{mood}"

    return "none"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MindMate Mental Health Chatbot")
    parser.add_argument("--backend", action="store_true",
                       help="Use backend API instead of local storage")
    parser.add_argument("--user-id", type=str,
                       help="Specify user ID (optional)")
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
        print("Create a .env file with: OPENAI_API_KEY=your_key_here")
        return

    # Get or generate user ID
    user_id = args.user_id or get_user_id_from_env()

    # Initialize enhanced chatbot
    db_kwargs = {}
    if args.backend:
        if args.api_url:
            db_kwargs['api_base_url'] = args.api_url
        if args.api_key:
            db_kwargs['api_key'] = args.api_key

    chatbot = EnhancedMindMateChatbot(openai_api_key, use_backend=args.backend, **db_kwargs)

    # Start user session
    session = chatbot.start_session(user_id)

    # Initialize assessment components
    assessment_client = AssessmentAPIClient()
    current_assessment = None

    # Welcome message - check if returning user
    if session.is_returning_user():
        print("Welcome back to MindMate! It's good to see you again.")
        print("How are you feeling today?")
    else:
        print("Hi! I'm MindMate. How are you feeling today?")

    print("(Type 'quit' to exit, 'help' for commands)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nTake care! Remember, you're not alone. Stay safe!")
                break
            elif user_input.lower() == 'help':
                print("""
**Available Commands:**
• 'clear' - Clear conversation (start fresh)
• 'mood' - View your mood tracking summary
• 'assessment' - Take a mental health assessment
• 'results' - Share external assessment results
• 'session' - View session information
• 'quit' - Exit the application
""")
                continue
            elif user_input.lower() == 'clear':
                # Start new session
                session = chatbot.start_session(user_id)
                print("\nConversation cleared. How can I support you today?")
                continue
            elif user_input.lower() == 'mood':
                mood_data = chatbot.get_mood_summary(session)
                if mood_data:
                    print("\nYour recent mood patterns:")
                    for date, moods in mood_data.items():
                        print(f"  {date}: {[m['mood'] for m in moods]}")
                else:
                    print("\nNo mood data tracked yet.")
                continue
            elif user_input.lower() == 'session':
                session_info = chatbot.get_session_info()
                print(f"\n**Session Information:**")
                print(f"User ID: {session_info.get('user_id', 'Unknown')}")
                print(f"Session Duration: {session_info.get('session_duration_minutes', 0):.1f} minutes")
                print(f"Returning User: {session_info.get('is_returning_user', False)}")
                print(f"Total Conversations: {session_info.get('user_profile', {}).get('conversation_count', 0)}")
                continue
            elif user_input.lower() == 'assessment':
                print("\n**Mental Health Assessment Options**")
                print("Which assessment would you like to take?")
                print("1. PHQ-9 (Depression screening)")
                print("2. GAD-7 (Anxiety screening)")
                print("3. Get external assessment link")
                assessment_choice = input("Enter 1, 2, or 3: ").strip()

                if assessment_choice == '1':
                    current_assessment = MockAssessmentSession('phq9')
                    print("\n**PHQ-9 Depression Assessment**")
                    print("*Important Disclaimer: This is a screening tool, not a diagnostic instrument.*")
                    print("\nI'll ask you 9 questions. Please respond with a number (0-3):")
                    print("0 = Not at all")
                    print("1 = Several days")
                    print("2 = More than half the days")
                    print("3 = Nearly every day")

                    question = current_assessment.get_current_question()
                    print(f"\nQuestion 1: {question['text']}")
                elif assessment_choice == '2':
                    current_assessment = MockAssessmentSession('gad7')
                    print("\n**GAD-7 Anxiety Assessment**")
                    print("*Important Disclaimer: This is a screening tool, not a diagnostic instrument.*")
                    print("\nI'll ask you 7 questions. Please respond with a number (0-3):")
                    print("0 = Not at all")
                    print("1 = Several days")
                    print("2 = More than half the days")
                    print("3 = Nearly every day")

                    question = current_assessment.get_current_question()
                    print(f"\nQuestion 1: {question['text']}")
                elif assessment_choice == '3':
                    print("\n**External Assessment Options**")
                    print("1. PHQ-9 Link:", assessment_client.get_assessment_link('phq9'))
                    print("2. GAD-7 Link:", assessment_client.get_assessment_link('gad7'))
                    print("\nAfter completing the external assessment, type 'results' to share them with me.")
                else:
                    print("Invalid choice. Please type 'assessment' again to start.")
                continue
            elif user_input.lower() == 'results':
                print("\n**Share External Assessment Results**")
                print("Please provide your assessment results:")

                assessment_type = input("Assessment type (phq9/gad7): ").strip().lower()
                if assessment_type not in ['phq9', 'gad7']:
                    print("Invalid assessment type. Please use 'phq9' or 'gad7'.")
                    continue

                try:
                    total_score = int(input("Total score: ").strip())
                    responses_input = input("Individual responses (comma-separated, optional): ").strip()

                    responses = None
                    if responses_input:
                        responses = [int(r.strip()) for r in responses_input.split(',')]

                    # Get chatbot analysis and store results
                    analysis = chatbot.analyze_assessment_results(assessment_type, total_score, responses, session)
                    print(f"\nMindMate: {analysis}")

                except ValueError:
                    print("Invalid input. Please enter valid numbers.")
                continue
            elif not user_input:
                continue

            # Handle active assessment
            if current_assessment and current_assessment.active:
                try:
                    response_num = int(user_input.strip())
                    if response_num not in [0, 1, 2, 3]:
                        print("Please enter a number between 0-3.")
                        continue

                    # Submit response
                    if current_assessment.submit_response(response_num):
                        if current_assessment.is_complete():
                            # Assessment complete - get results and analyze
                            results = current_assessment.get_results()
                            print("\n✅ Assessment completed!")

                            # Get chatbot analysis and store results
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
                            question = current_assessment.get_current_question()
                            question_num = current_assessment.current_question + 1
                            print(f"\nQuestion {question_num}: {question['text']}")
                    else:
                        print("Invalid response. Please enter a number between 0-3.")

                except ValueError:
                    print("Please enter a number between 0-3.")
                continue

            # Input validation
            is_valid, warning = validate_input(user_input)
            if not is_valid:
                print(f"\nMindMate: {warning}")
                continue

            # Show typing indicator
            show_typing_indicator()

            try:
                # Get chatbot response with session context
                response = chatbot.chat(user_input, session)
                print(f"MindMate: {response}")

                # Check for additional triggers (booking and resources)
                if not current_assessment:
                    trigger = analyze_triggers(user_input)

                    if trigger == "booking":
                        print(suggest_booking())
                    elif trigger.startswith("resources_"):
                        resource_type = trigger.split("_")[1]
                        print(share_resources(resource_type))

            except Exception as api_error:
                print(f"MindMate: I'm having trouble connecting right now. Please try again in a moment.")
                print("If you're in crisis, please call 988 for immediate support.")

        except KeyboardInterrupt:
            print("\n\nTake care! Remember, you're not alone. Stay safe!")
            break
        except Exception as e:
            print(f"\nERROR: Something went wrong. Please try again.")
            print("If you're in crisis, please call 988 for immediate support.")

if __name__ == "__main__":
    main()