# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindMate is a mental health chatbot project with both a command-line interface and a Django backend. The chatbot provides empathetic conversations, mental health assessments (PHQ-9, GAD-7), crisis intervention, and resource recommendations.

## Architecture

### Core Components
- **main.py**: CLI interface with conversation flow, input validation, and trigger detection
- **chatbot.py**: `MindMateChatbot` class handling OpenAI API integration, mood tracking, and response enhancement
- **assessment_api.py**: Assessment management with `AssessmentAPIClient` and `MockAssessmentSession` classes
- **backend/**: Django REST API (planned/partial implementation)

### Key Features
- Crisis detection and intervention with emergency resources
- PHQ-9 (depression) and GAD-7 (anxiety) assessments
- Mood tracking and analysis
- Intelligent suggestion system for assessments and resources
- Input validation and content filtering

## Development Commands

### Running the Application
```bash
# Set up environment
python -m venv mindmate_env
source mindmate_env/bin/activate  # Windows: mindmate_env\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run original CLI chatbot (legacy)
python main.py

# Run enhanced CLI chatbot with database integration
python main_enhanced.py

# Run multilingual chatbot (English, Hindi, Tamil)
python main_multilingual.py

# Run with backend API (when available)
python main_enhanced.py --backend --api-url http://localhost:8000

# Run multilingual with specific language
python main_multilingual.py --language hi  # Hindi
python main_multilingual.py --language ta  # Tamil

# Set OpenAI API key in .env file
OPENAI_API_KEY=your_key_here
```

### Backend Development (Django)
```bash
cd backend
python manage.py runserver
python manage.py migrate
python manage.py test
```

### CLI Commands Available to Users
- `quit/exit/bye`: Exit application
- `clear`: Clear conversation history
- `mood`: View mood tracking summary
- `assessment`: Start PHQ-9 or GAD-7 assessment
- `results`: Share external assessment results for analysis

## Code Architecture

### Conversation Flow
1. **Input Validation** (`validate_input()` in main.py)
2. **Crisis Detection** (`detect_crisis_keywords()` in chatbot.py)
3. **OpenAI API Call** (`chat()` method)
4. **Trigger Analysis** (`analyze_triggers()` in main.py and `enhance_response_with_suggestions()` in chatbot.py)
5. **Response Enhancement** with assessments, resources, or booking suggestions

### Assessment System
- External API integration via `AssessmentAPIClient`
- Mock session management with `MockAssessmentSession`
- Automatic score analysis and interpretation
- Support for both internal and external assessment workflows

### Safety Features
- Multi-layer crisis detection with immediate resource provision
- Input content filtering for inappropriate material
- Emergency contact information (988, Crisis Text Line)
- Professional help disclaimers and referrals

## Important Implementation Notes

### Crisis Handling
The system prioritizes safety through:
- Regex-based crisis keyword detection
- Immediate display of emergency resources
- Bypassing normal conversation flow in crisis mode

### Assessment Integration
- Supports both built-in assessment flows and external assessment links
- Intelligent score detection from user messages
- Contextual assessment suggestions based on user sentiment

### Mood Tracking
- Automatic mood extraction from conversation
- Daily mood summaries with timestamps
- Integration with assessment suggestions

### API Integration
- OpenAI GPT-4o-mini for conversation generation
- Mock assessment API with plans for real external integration
- Proper error handling for API failures

## File Structure Context

```
├── main.py                    # Original CLI entry point (legacy)
├── main_enhanced.py           # Enhanced CLI with database integration
├── main_multilingual.py       # Multilingual CLI (English, Hindi, Tamil)
├── chatbot.py                # Original chatbot logic (legacy)
├── enhanced_chatbot.py       # Enhanced chatbot with session management
├── multilingual_chatbot.py   # Multilingual chatbot with cultural adaptation
├── session_manager.py        # User session and context management
├── database_interface.py     # Database abstraction layer
├── language_manager.py       # Language selection and localization
├── assessment_api.py         # Assessment system and external API handling
├── languages/               # Localization files (en.json, hi.json, ta.json)
├── backend/                  # Django REST API (partial implementation)
│   ├── requirements.txt      # Django, DRF, OpenAI, PostgreSQL dependencies
│   └── mindmate/            # Django project configuration
├── user_data/               # Local file storage for development
└── .env                     # Environment variables (OpenAI API key)
```

## Integration Architecture

### Database Abstraction Layer
The `database_interface.py` provides a clean abstraction that allows switching between:
- **Local File Storage** (`LocalFileStorage`): JSON files for development
- **Backend API Storage** (`BackendAPIStorage`): REST API calls for production

### Session Management
The `session_manager.py` handles:
- User identification and session persistence
- Conversation context building from history
- Mood and assessment tracking across sessions
- Session serialization for API transmission

### Enhanced Components
- **`enhanced_chatbot.py`**: Session-aware chatbot with persistent context
- **`main_enhanced.py`**: CLI interface with backend integration options
- **Command-line flags**: `--backend`, `--user-id`, `--api-url` for flexible deployment

### Multilingual Support
The `language_manager.py` and `multilingual_chatbot.py` provide:
- **Language Selection**: User chooses from English, Hindi, Tamil at startup
- **Cultural Adaptation**: Localized crisis resources, coping strategies, and conversation styles
- **Assessment Translation**: PHQ-9 and GAD-7 questions in all supported languages
- **Smart Detection**: Crisis and mood detection patterns for all languages
- **Persistent Preferences**: User language choice saved across sessions

## MindMate Chatbot Instructions

### Overview
MindMate is a supportive mental health chatbot designed to:
- Provide empathetic and safe conversations
- Encourage positive coping strategies and emotional regulation
- Suggest assessments, resources, or booking a counselor when appropriate
- Escalate to **crisis mode** when harmful or suicidal language is detected

MindMate is **not a substitute for professional care** and never provides diagnoses or medical advice.

### Conversation Flow

#### 1. Entry Point
- **Welcome message**: "Hi! I'm MindMate. How are you feeling today?"
- Load chat history if available

#### 2. Input Validation
- Check if input is appropriate
- If inappropriate → return content warning: "Please keep our conversation supportive and safe."

#### 3. Message Processing
- Forward valid input to AI model
- Generate empathetic response

#### 4. Trigger Detection
After each response, analyze for **action triggers**:
- **Crisis detected** → suicide, self-harm, hopelessness, "can't go on"
- **Suggest assessment** → user mentions anxiety, stress, or uncertainty
- **Suggest booking** → user expresses desire for professional help
- **Share resources** → user asks for coping tools, tips, or techniques
- **None** → continue conversation normally

#### 5. Trigger Responses
- **Crisis protocol**: Show emergency resources + counselor contact, urge immediate help
- **Assessment suggestion**: Offer optional mental health screening (PHQ-9, GAD-7)
- **Booking suggestion**: Encourage talking to a counselor
- **Resource recommendation**: Provide self-help tools, coping strategies, or exercises
- **No trigger detected**: Continue with supportive, empathetic dialogue

#### 6. Chat States
- **Idle** → waiting for input
- **Typing** → "MindMate is typing…"
- **Processing** → "Thinking…"
- **Error** → apologize and suggest retry
- **Escalated (Crisis mode)** → display crisis resources immediately

### Style Guide
- Always empathetic, warm, and non-judgmental
- Prioritize **validation** ("It makes sense you feel this way") before giving suggestions
- Use short, clear sentences
- Never push; always offer choices ("Would you like to try…?")

### Safety Rules
- Never provide medical or diagnostic advice
- Always display disclaimers when suggesting assessments or bookings
- In crisis mode, prioritize safety over continuing normal conversation
- Never ignore or downplay harmful language
