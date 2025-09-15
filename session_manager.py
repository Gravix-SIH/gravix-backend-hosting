"""
Session Manager for MindMate Chatbot
Handles user identification, session state, and context management
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database_interface import DatabaseInterface, get_database_interface

class UserSession:
    """Represents a user session with context and state."""

    def __init__(self, user_id: str, database: DatabaseInterface):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.database = database
        self.session_start = datetime.now()
        self.last_activity = datetime.now()
        self.context = {}
        self.current_assessment = None

        # Load user profile and update activity
        self.user_profile = database.get_user_profile(user_id)
        database.update_user_activity(user_id)

    def get_conversation_context(self, limit: int = 10) -> str:
        """Build conversation context from recent history for OpenAI prompt."""
        recent_conversations = self.database.get_recent_conversations(self.user_id, limit)

        if not recent_conversations:
            return ""

        context_lines = []
        context_lines.append("Previous conversation context:")

        for conv in recent_conversations[-5:]:  # Last 5 exchanges
            timestamp = conv.get('timestamp', '')
            if timestamp:
                date_str = timestamp[:10]  # YYYY-MM-DD
                context_lines.append(f"[{date_str}] User: {conv['message']}")
                context_lines.append(f"[{date_str}] MindMate: {conv['response'][:100]}...")

                if conv.get('mood_detected'):
                    context_lines.append(f"    (Mood detected: {conv['mood_detected']})")
                if conv.get('crisis_detected'):
                    context_lines.append("    (Crisis intervention activated)")

        return "\n".join(context_lines)

    def get_assessment_context(self) -> str:
        """Build assessment context from user's history."""
        assessments = self.database.get_user_assessments(self.user_id, limit=5)

        if not assessments:
            return ""

        context_lines = []
        context_lines.append("Recent assessment history:")

        for assessment in assessments:
            timestamp = assessment.get('timestamp', '')
            date_str = timestamp[:10] if timestamp else 'Unknown date'
            assessment_type = assessment.get('type', 'Unknown')
            score = assessment.get('score', 'Unknown')

            context_lines.append(f"[{date_str}] {assessment_type.upper()}: {score}")

        return "\n".join(context_lines)

    def get_mood_context(self) -> str:
        """Build mood context from recent tracking."""
        mood_summary = self.database.get_mood_summary(self.user_id, days=7)

        if not mood_summary:
            return ""

        context_lines = []
        context_lines.append("Recent mood patterns (last 7 days):")

        for date, moods in list(mood_summary.items())[-3:]:  # Last 3 days
            mood_list = [m['mood'] for m in moods]
            context_lines.append(f"[{date}]: {', '.join(mood_list)}")

        return "\n".join(context_lines)

    def build_full_context(self) -> str:
        """Build complete context for AI model."""
        context_parts = []

        # User profile context
        profile = self.user_profile
        total_conversations = profile.get('conversation_count', 0)
        if total_conversations > 0:
            context_parts.append(f"User has had {total_conversations} previous conversations.")

        # Add conversation context
        conv_context = self.get_conversation_context()
        if conv_context:
            context_parts.append(conv_context)

        # Add assessment context
        assessment_context = self.get_assessment_context()
        if assessment_context:
            context_parts.append(assessment_context)

        # Add mood context
        mood_context = self.get_mood_context()
        if mood_context:
            context_parts.append(mood_context)

        if context_parts:
            return "\n\n".join(context_parts) + "\n\nBased on this context, respond appropriately:"

        return ""

    def store_conversation(self, message: str, response: str, mood_detected: str = None,
                          crisis_detected: bool = False) -> str:
        """Store conversation in database and update session state."""
        self.last_activity = datetime.now()

        conversation_id = self.database.store_conversation(
            self.user_id, message, response, mood_detected, crisis_detected
        )

        # Store in session context for immediate use
        self.context['last_message'] = message
        self.context['last_response'] = response
        self.context['last_mood'] = mood_detected
        self.context['last_crisis'] = crisis_detected

        return conversation_id

    def store_assessment(self, assessment_type: str, score: int, responses: list) -> str:
        """Store assessment results."""
        self.last_activity = datetime.now()

        assessment_id = self.database.store_assessment(
            self.user_id, assessment_type, score, responses
        )

        # Update session context
        self.context['last_assessment'] = {
            'type': assessment_type,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }

        return assessment_id

    def store_mood(self, mood: str, intensity: int = None, context: str = None) -> str:
        """Store mood tracking data."""
        self.last_activity = datetime.now()

        mood_id = self.database.store_mood_tracking(
            self.user_id, mood, intensity, context
        )

        # Update session context
        self.context['last_mood_tracked'] = {
            'mood': mood,
            'intensity': intensity,
            'timestamp': datetime.now().isoformat()
        }

        return mood_id

    def is_returning_user(self) -> bool:
        """Check if this is a returning user."""
        return self.user_profile.get('conversation_count', 0) > 0

    def get_session_duration(self) -> timedelta:
        """Get current session duration."""
        return datetime.now() - self.session_start

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session for API transmission."""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'context': self.context,
            'user_profile': self.user_profile,
            'is_returning_user': self.is_returning_user(),
            'session_duration_minutes': self.get_session_duration().total_seconds() / 60
        }

class SessionManager:
    """Manages user sessions and provides session-aware database operations."""

    def __init__(self, use_backend: bool = False, **db_kwargs):
        self.database = get_database_interface(use_backend, **db_kwargs)
        self.active_sessions = {}  # session_id -> UserSession

    def create_session(self, user_id: str = None) -> UserSession:
        """Create a new user session."""
        if user_id is None:
            user_id = str(uuid.uuid4())

        session = UserSession(user_id, self.database)
        self.active_sessions[session.session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get existing session by ID."""
        return self.active_sessions.get(session_id)

    def get_or_create_session(self, user_id: str = None, session_id: str = None) -> UserSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            return session

        return self.create_session(user_id)

    def cleanup_inactive_sessions(self, hours: int = 24) -> int:
        """Remove sessions inactive for specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        inactive_sessions = []

        for session_id, session in self.active_sessions.items():
            if session.last_activity < cutoff_time:
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            del self.active_sessions[session_id]

        return len(inactive_sessions)

    def get_active_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self.active_sessions)

def get_user_id_from_env() -> str:
    """Get user ID from environment or generate new one."""
    # For CLI usage - you could store in a local file or env var
    user_file = ".user_id"

    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            return f.read().strip()
    else:
        # Generate new user ID for CLI usage
        user_id = str(uuid.uuid4())
        with open(user_file, 'w') as f:
            f.write(user_id)
        return user_id