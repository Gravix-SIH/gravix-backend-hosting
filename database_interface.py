"""
Database Interface for MindMate Chatbot
Provides abstraction layer for data persistence that can be swapped between
local storage (development) and backend API (production)
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid

class DatabaseInterface(ABC):
    """Abstract interface for data storage operations."""

    @abstractmethod
    def store_conversation(self, user_id: str, message: str, response: str,
                          mood_detected: str = None, crisis_detected: bool = False) -> str:
        """Store a conversation exchange."""
        pass

    @abstractmethod
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations for context."""
        pass

    @abstractmethod
    def store_assessment(self, user_id: str, assessment_type: str,
                        score: int, responses: List[int]) -> str:
        """Store assessment results."""
        pass

    @abstractmethod
    def get_user_assessments(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's assessment history."""
        pass

    @abstractmethod
    def store_mood_tracking(self, user_id: str, mood: str, intensity: int = None,
                           context: str = None) -> str:
        """Store mood tracking data."""
        pass

    @abstractmethod
    def get_mood_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get mood tracking summary."""
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile information."""
        pass

    @abstractmethod
    def update_user_activity(self, user_id: str) -> None:
        """Update user's last activity timestamp."""
        pass

class LocalFileStorage(DatabaseInterface):
    """Local file-based storage for development."""

    def __init__(self, data_dir: str = "./user_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_user_file(self, user_id: str, data_type: str) -> str:
        """Get file path for user data."""
        return os.path.join(self.data_dir, f"{user_id}_{data_type}.json")

    def _load_user_data(self, user_id: str, data_type: str) -> List[Dict]:
        """Load user data from file."""
        file_path = self._get_user_file(user_id, data_type)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []

    def _save_user_data(self, user_id: str, data_type: str, data: List[Dict]) -> None:
        """Save user data to file."""
        file_path = self._get_user_file(user_id, data_type)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def store_conversation(self, user_id: str, message: str, response: str,
                          mood_detected: str = None, crisis_detected: bool = False) -> str:
        conversations = self._load_user_data(user_id, "conversations")

        conversation_id = str(uuid.uuid4())
        conversation = {
            "id": conversation_id,
            "message": message,
            "response": response,
            "mood_detected": mood_detected,
            "crisis_detected": crisis_detected,
            "timestamp": datetime.now().isoformat()
        }

        conversations.append(conversation)

        # Keep only last 100 conversations
        if len(conversations) > 100:
            conversations = conversations[-100:]

        self._save_user_data(user_id, "conversations", conversations)
        return conversation_id

    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        conversations = self._load_user_data(user_id, "conversations")
        return conversations[-limit:] if conversations else []

    def store_assessment(self, user_id: str, assessment_type: str,
                        score: int, responses: List[int]) -> str:
        assessments = self._load_user_data(user_id, "assessments")

        assessment_id = str(uuid.uuid4())
        assessment = {
            "id": assessment_id,
            "type": assessment_type,
            "score": score,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }

        assessments.append(assessment)
        self._save_user_data(user_id, "assessments", assessments)
        return assessment_id

    def get_user_assessments(self, user_id: str, limit: int = 10) -> List[Dict]:
        assessments = self._load_user_data(user_id, "assessments")
        return assessments[-limit:] if assessments else []

    def store_mood_tracking(self, user_id: str, mood: str, intensity: int = None,
                           context: str = None) -> str:
        mood_data = self._load_user_data(user_id, "mood_tracking")

        mood_id = str(uuid.uuid4())
        mood_entry = {
            "id": mood_id,
            "mood": mood,
            "intensity": intensity,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

        mood_data.append(mood_entry)

        # Keep only last 200 mood entries
        if len(mood_data) > 200:
            mood_data = mood_data[-200:]

        self._save_user_data(user_id, "mood_tracking", mood_data)
        return mood_id

    def get_mood_summary(self, user_id: str, days: int = 30) -> Dict:
        mood_data = self._load_user_data(user_id, "mood_tracking")

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_moods = []

        for entry in mood_data:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date >= cutoff_date:
                recent_moods.append(entry)

        # Group by date
        mood_by_date = {}
        for entry in recent_moods:
            date_str = entry["timestamp"][:10]  # YYYY-MM-DD
            if date_str not in mood_by_date:
                mood_by_date[date_str] = []
            mood_by_date[date_str].append({
                "mood": entry["mood"],
                "intensity": entry.get("intensity"),
                "timestamp": entry["timestamp"]
            })

        return mood_by_date

    def get_user_profile(self, user_id: str) -> Dict:
        profile_data = self._load_user_data(user_id, "profile")
        if profile_data:
            return profile_data[0]

        # Create default profile
        default_profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "conversation_count": 0,
            "assessment_count": 0
        }
        self._save_user_data(user_id, "profile", [default_profile])
        return default_profile

    def update_user_activity(self, user_id: str) -> None:
        profile = self.get_user_profile(user_id)
        profile["last_active"] = datetime.now().isoformat()
        profile["conversation_count"] = profile.get("conversation_count", 0) + 1
        self._save_user_data(user_id, "profile", [profile])

class BackendAPIStorage(DatabaseInterface):
    """Backend API storage for production (to be implemented)."""

    def __init__(self, api_base_url: str, api_key: str = None):
        self.api_base_url = api_base_url
        self.api_key = api_key
        # Will be implemented when backend is ready

    def store_conversation(self, user_id: str, message: str, response: str,
                          mood_detected: str = None, crisis_detected: bool = False) -> str:
        # TODO: Implement API call to backend
        # POST /api/conversations/
        raise NotImplementedError("Backend API not yet implemented")

    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        # TODO: Implement API call to backend
        # GET /api/users/{user_id}/conversations/?limit={limit}
        raise NotImplementedError("Backend API not yet implemented")

    def store_assessment(self, user_id: str, assessment_type: str,
                        score: int, responses: List[int]) -> str:
        # TODO: Implement API call to backend
        # POST /api/assessments/
        raise NotImplementedError("Backend API not yet implemented")

    def get_user_assessments(self, user_id: str, limit: int = 10) -> List[Dict]:
        # TODO: Implement API call to backend
        # GET /api/users/{user_id}/assessments/?limit={limit}
        raise NotImplementedError("Backend API not yet implemented")

    def store_mood_tracking(self, user_id: str, mood: str, intensity: int = None,
                           context: str = None) -> str:
        # TODO: Implement API call to backend
        # POST /api/mood-tracking/
        raise NotImplementedError("Backend API not yet implemented")

    def get_mood_summary(self, user_id: str, days: int = 30) -> Dict:
        # TODO: Implement API call to backend
        # GET /api/users/{user_id}/mood-summary/?days={days}
        raise NotImplementedError("Backend API not yet implemented")

    def get_user_profile(self, user_id: str) -> Dict:
        # TODO: Implement API call to backend
        # GET /api/users/{user_id}/profile/
        raise NotImplementedError("Backend API not yet implemented")

    def update_user_activity(self, user_id: str) -> None:
        # TODO: Implement API call to backend
        # PATCH /api/users/{user_id}/activity/
        raise NotImplementedError("Backend API not yet implemented")

def get_database_interface(use_backend: bool = False, **kwargs) -> DatabaseInterface:
    """Factory function to get appropriate database interface."""
    if use_backend:
        return BackendAPIStorage(**kwargs)
    else:
        return LocalFileStorage(**kwargs)