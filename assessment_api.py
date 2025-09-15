"""
Assessment API Client for MindMate
Handles external API integration for mental health assessments
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

class AssessmentAPIClient:
    def __init__(self, api_base_url: str = "https://api.mentalhealth-assessment.com", api_key: str = None):
        """Initialize the assessment API client."""
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })

    def get_phq9_questions(self) -> List[Dict]:
        """Get PHQ-9 questions from external API."""
        # Mock implementation - replace with real API call
        return [
            {
                "id": 1,
                "text": "Over the last 2 weeks, how often have you been bothered by little interest or pleasure in doing things?",
                "scale": "0-3"
            },
            {
                "id": 2,
                "text": "Over the last 2 weeks, how often have you been bothered by feeling down, depressed, or hopeless?",
                "scale": "0-3"
            },
            {
                "id": 3,
                "text": "Over the last 2 weeks, how often have you been bothered by trouble falling or staying asleep, or sleeping too much?",
                "scale": "0-3"
            },
            {
                "id": 4,
                "text": "Over the last 2 weeks, how often have you been bothered by feeling tired or having little energy?",
                "scale": "0-3"
            },
            {
                "id": 5,
                "text": "Over the last 2 weeks, how often have you been bothered by poor appetite or overeating?",
                "scale": "0-3"
            },
            {
                "id": 6,
                "text": "Over the last 2 weeks, how often have you been bothered by feeling bad about yourself or that you are a failure or have let yourself or your family down?",
                "scale": "0-3"
            },
            {
                "id": 7,
                "text": "Over the last 2 weeks, how often have you been bothered by trouble concentrating on things, such as reading the newspaper or watching television?",
                "scale": "0-3"
            },
            {
                "id": 8,
                "text": "Over the last 2 weeks, how often have you been bothered by moving or speaking so slowly that other people could have noticed? Or the opposite being so fidgety or restless that you have been moving around a lot more than usual?",
                "scale": "0-3"
            },
            {
                "id": 9,
                "text": "Over the last 2 weeks, how often have you been bothered by thoughts that you would be better off dead, or of hurting yourself?",
                "scale": "0-3"
            }
        ]

    def get_gad7_questions(self) -> List[Dict]:
        """Get GAD-7 questions from external API."""
        # Mock implementation - replace with real API call
        return [
            {
                "id": 1,
                "text": "Over the last 2 weeks, how often have you been bothered by feeling nervous, anxious, or on edge?",
                "scale": "0-3"
            },
            {
                "id": 2,
                "text": "Over the last 2 weeks, how often have you been bothered by not being able to stop or control worrying?",
                "scale": "0-3"
            },
            {
                "id": 3,
                "text": "Over the last 2 weeks, how often have you been bothered by worrying too much about different things?",
                "scale": "0-3"
            },
            {
                "id": 4,
                "text": "Over the last 2 weeks, how often have you been bothered by trouble relaxing?",
                "scale": "0-3"
            },
            {
                "id": 5,
                "text": "Over the last 2 weeks, how often have you been bothered by being so restless that it is hard to sit still?",
                "scale": "0-3"
            },
            {
                "id": 6,
                "text": "Over the last 2 weeks, how often have you been bothered by becoming easily annoyed or irritable?",
                "scale": "0-3"
            },
            {
                "id": 7,
                "text": "Over the last 2 weeks, how often have you been bothered by feeling afraid, as if something awful might happen?",
                "scale": "0-3"
            }
        ]

    def start_assessment_session(self, assessment_type: str, user_id: str = None) -> Dict:
        """Start a new assessment session."""
        session_id = str(uuid.uuid4())

        # Mock API response - replace with real API call
        mock_response = {
            "session_id": session_id,
            "assessment_type": assessment_type,
            "user_id": user_id or "anonymous",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "questions": self.get_phq9_questions() if assessment_type == "phq9" else self.get_gad7_questions(),
            "current_question": 0,
            "api_url": f"{self.api_base_url}/assessment/{session_id}"
        }

        # In real implementation, this would be:
        # response = self.session.post(f"{self.api_base_url}/assessment/start", json={
        #     "assessment_type": assessment_type,
        #     "user_id": user_id
        # })
        # return response.json()

        return mock_response

    def submit_assessment_responses(self, session_id: str, responses: List[int]) -> Dict:
        """Submit all assessment responses and get results."""
        # Mock API response - replace with real API call
        total_score = sum(responses)

        mock_result = {
            "session_id": session_id,
            "total_score": total_score,
            "responses": responses,
            "completed_at": datetime.now().isoformat(),
            "severity_level": self._calculate_severity(total_score, len(responses)),
            "recommendations": self._get_recommendations(total_score, len(responses)),
            "risk_flags": self._check_risk_flags(responses)
        }

        # In real implementation, this would be:
        # response = self.session.post(f"{self.api_base_url}/assessment/{session_id}/submit", json={
        #     "responses": responses
        # })
        # return response.json()

        return mock_result

    def get_assessment_link(self, assessment_type: str, user_id: str = None) -> str:
        """Generate a link to external assessment platform."""
        session = self.start_assessment_session(assessment_type, user_id)
        return session["api_url"]

    def _calculate_severity(self, score: int, num_questions: int) -> str:
        """Calculate severity level based on score."""
        if num_questions == 9:  # PHQ-9
            if score <= 4:
                return "minimal"
            elif score <= 9:
                return "mild"
            elif score <= 14:
                return "moderate"
            elif score <= 19:
                return "moderately_severe"
            else:
                return "severe"
        elif num_questions == 7:  # GAD-7
            if score <= 4:
                return "minimal"
            elif score <= 9:
                return "mild"
            elif score <= 14:
                return "moderate"
            else:
                return "severe"
        return "unknown"

    def _get_recommendations(self, score: int, num_questions: int) -> List[str]:
        """Get recommendations based on score."""
        severity = self._calculate_severity(score, num_questions)

        recommendations = {
            "minimal": [
                "Continue with healthy lifestyle habits",
                "Regular exercise and good sleep schedule",
                "Stay connected with support systems"
            ],
            "mild": [
                "Consider self-care strategies",
                "Monitor symptoms over time",
                "Reach out if symptoms worsen"
            ],
            "moderate": [
                "Consider speaking with a healthcare provider",
                "Explore therapy options",
                "Implement stress management techniques"
            ],
            "moderately_severe": [
                "Strongly recommend professional consultation",
                "Consider therapy and/or medication evaluation",
                "Engage support systems"
            ],
            "severe": [
                "Seek professional help immediately",
                "Contact healthcare provider",
                "Consider intensive treatment options"
            ]
        }

        return recommendations.get(severity, ["Consult with healthcare professional"])

    def _check_risk_flags(self, responses: List[int]) -> List[str]:
        """Check for specific risk indicators in responses."""
        flags = []

        # Check for suicidal ideation (PHQ-9 question 9)
        if len(responses) >= 9 and responses[8] > 0:
            flags.append("suicidal_ideation")

        # Check for severe symptoms
        if any(response >= 3 for response in responses):
            flags.append("severe_symptoms")

        return flags

class MockAssessmentSession:
    """Mock class to simulate assessment session management."""

    def __init__(self, assessment_type: str):
        self.assessment_type = assessment_type
        self.questions = []
        self.current_question = 0
        self.responses = []
        self.active = True

        # Load questions
        client = AssessmentAPIClient()
        if assessment_type == "phq9":
            self.questions = client.get_phq9_questions()
        elif assessment_type == "gad7":
            self.questions = client.get_gad7_questions()

    def get_current_question(self) -> Optional[Dict]:
        """Get the current question."""
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None

    def submit_response(self, response: int) -> bool:
        """Submit response to current question."""
        if 0 <= response <= 3:
            self.responses.append(response)
            self.current_question += 1
            return True
        return False

    def is_complete(self) -> bool:
        """Check if assessment is complete."""
        return self.current_question >= len(self.questions)

    def get_results(self) -> Dict:
        """Get assessment results."""
        if not self.is_complete():
            return {"error": "Assessment not complete"}

        client = AssessmentAPIClient()
        return client.submit_assessment_responses("mock_session", self.responses)