"""
Language Management System for MindMate
Handles language selection, localization, and cultural adaptation
"""

import json
import os
from typing import Dict, Optional, Any
from enum import Enum

class SupportedLanguage(Enum):
    """Supported languages for MindMate."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"

class LanguageManager:
    """Manages language selection and localized content."""

    def __init__(self, languages_dir: str = "languages"):
        self.languages_dir = languages_dir
        self.current_language = SupportedLanguage.ENGLISH
        self.translations = {}
        self.cultural_contexts = {}

        # Create languages directory if it doesn't exist
        os.makedirs(languages_dir, exist_ok=True)

        # Load all language files
        self.load_all_languages()

    def load_all_languages(self):
        """Load translation files for all supported languages."""
        for lang in SupportedLanguage:
            try:
                self.load_language(lang)
            except FileNotFoundError:
                print(f"Warning: Language file for {lang.value} not found")

    def load_language(self, language: SupportedLanguage):
        """Load translation file for specific language."""
        file_path = os.path.join(self.languages_dir, f"{language.value}.json")

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.translations[language] = data.get('translations', {})
                self.cultural_contexts[language] = data.get('cultural_context', {})
        else:
            # Create default structure if file doesn't exist
            self.translations[language] = {}
            self.cultural_contexts[language] = {}

    def set_language(self, language: SupportedLanguage):
        """Set the current active language."""
        self.current_language = language

    def get_language_from_code(self, code: str) -> Optional[SupportedLanguage]:
        """Get SupportedLanguage enum from language code."""
        for lang in SupportedLanguage:
            if lang.value == code:
                return lang
        return None

    def get_text(self, key: str, **kwargs) -> str:
        """Get localized text for the current language."""
        translations = self.translations.get(self.current_language, {})
        text = translations.get(key, f"[Missing: {key}]")

        # Handle string formatting
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted text if formatting fails

        return text

    def get_cultural_context(self, key: str) -> Any:
        """Get cultural context information for current language."""
        context = self.cultural_contexts.get(self.current_language, {})
        return context.get(key, {})

    def get_crisis_resources(self) -> Dict[str, str]:
        """Get localized crisis resources."""
        return self.get_cultural_context('crisis_resources')

    def get_mental_health_resources(self) -> Dict[str, Any]:
        """Get localized mental health resources."""
        return self.get_cultural_context('mental_health_resources')

    def get_system_prompt(self, base_prompt: str) -> str:
        """Get culturally adapted system prompt for AI."""
        cultural_instructions = self.get_cultural_context('ai_instructions')

        if not cultural_instructions:
            return base_prompt

        # Add cultural context to the base prompt
        adapted_prompt = base_prompt + "\n\n" + cultural_instructions.get('additional_context', '')

        # Add language instruction
        lang_instruction = cultural_instructions.get('language_instruction', '')
        if lang_instruction:
            adapted_prompt += f"\n\n{lang_instruction}"

        return adapted_prompt

    def show_language_selection(self) -> SupportedLanguage:
        """Display language selection menu and get user choice."""
        print("\n" + "="*50)
        print("Welcome to MindMate / MindMate में आपका स्वागत है / MindMate-க்கு வரவேற்கிறோம்")
        print("="*50)
        print("\nPlease select your language / कृपया अपनी भाषा चुनें / தயவுசெய்து உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்:")
        print("\n1. English")
        print("2. हिंदी (Hindi)")
        print("3. தமிழ் (Tamil)")

        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()

                if choice == "1":
                    return SupportedLanguage.ENGLISH
                elif choice == "2":
                    return SupportedLanguage.HINDI
                elif choice == "3":
                    return SupportedLanguage.TAMIL
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
                    print("अमान्य विकल्प। कृपया 1, 2, या 3 दर्ज करें।")
                    print("தவறான தேர்வு. தயவுசெய்து 1, 2, அல்லது 3 ஐ உள்ளிடவும்.")

            except KeyboardInterrupt:
                print("\nGoodbye! / अलविदा! / வணக்கம்!")
                exit(0)

    def get_language_display_name(self, language: SupportedLanguage = None) -> str:
        """Get display name for language."""
        if language is None:
            language = self.current_language

        names = {
            SupportedLanguage.ENGLISH: "English",
            SupportedLanguage.HINDI: "हिंदी",
            SupportedLanguage.TAMIL: "தமிழ்"
        }
        return names.get(language, "Unknown")

    def save_user_language_preference(self, user_id: str, language: SupportedLanguage):
        """Save user's language preference to file."""
        prefs_file = "user_language_preferences.json"

        # Load existing preferences
        preferences = {}
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)

        # Update and save
        preferences[user_id] = language.value
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)

    def load_user_language_preference(self, user_id: str) -> Optional[SupportedLanguage]:
        """Load user's saved language preference."""
        prefs_file = "user_language_preferences.json"

        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)

                lang_code = preferences.get(user_id)
                if lang_code:
                    return self.get_language_from_code(lang_code)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return None

    def get_assessment_questions(self, assessment_type: str) -> list:
        """Get localized assessment questions."""
        assessments = self.get_cultural_context('assessments')
        return assessments.get(assessment_type, {}).get('questions', [])

    def get_assessment_instructions(self, assessment_type: str) -> str:
        """Get localized assessment instructions."""
        assessments = self.get_cultural_context('assessments')
        return assessments.get(assessment_type, {}).get('instructions', '')

    def get_coping_strategies(self, mood: str) -> str:
        """Get culturally appropriate coping strategies."""
        strategies = self.get_cultural_context('coping_strategies')
        return strategies.get(mood, self.get_text('coping_general'))

# Global language manager instance
language_manager = LanguageManager()