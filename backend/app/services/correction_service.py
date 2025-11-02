from typing import Dict, List, Optional
from app.services.llm_service import LLMService
from app.database import get_db
from app.models import CorrectionCreate


class CorrectionService:
    """Service for handling pronunciation and grammar corrections"""

    def __init__(self):
        self.llm_service = LLMService()

    async def analyze_text(self, text: str) -> Dict:
        """
        Analyze user's text for errors and improvements

        Args:
            text: User's input text

        Returns:
            Analysis result with corrections
        """
        analysis = await self.llm_service.analyze_and_correct(text)
        return analysis

    async def save_corrections(
        self,
        session_id: str,
        conversation_id: str,
        corrections_data: List[Dict]
    ) -> List:
        """
        Save corrections to database

        Args:
            session_id: Session ID
            conversation_id: Conversation ID
            corrections_data: List of correction dictionaries

        Returns:
            List of saved correction records
        """
        try:
            db = get_db()
            saved_corrections = []

            for correction in corrections_data:
                correction_record = await db.correction.create(
                    data={
                        "sessionId": session_id,
                        "conversationId": conversation_id,
                        "correctionType": correction.get("type", "grammar"),
                        "originalText": correction.get("original", ""),
                        "correctedText": correction.get("corrected", ""),
                        "explanation": correction.get("explanation"),
                        "severity": correction.get("severity", "medium")
                    }
                )
                saved_corrections.append(correction_record)

            return saved_corrections

        except Exception as e:
            print(f"Error saving corrections: {e}")
            return []

    async def get_session_corrections(self, session_id: str) -> List:
        """
        Get all corrections for a session

        Args:
            session_id: Session ID

        Returns:
            List of corrections
        """
        try:
            db = get_db()
            corrections = await db.correction.find_many(
                where={"sessionId": session_id},
                order={"createdAt": "desc"}
            )
            return corrections

        except Exception as e:
            print(f"Error getting corrections: {e}")
            return []

    async def get_correction_stats(self, user_id: str) -> Dict:
        """
        Get correction statistics for a user

        Args:
            user_id: User ID

        Returns:
            Statistics dictionary
        """
        try:
            db = get_db()

            # Get all user sessions
            sessions = await db.session.find_many(
                where={"userId": user_id},
                select={"id": True}
            )

            session_ids = [s.id for s in sessions]

            # Get all corrections
            corrections = await db.correction.find_many(
                where={"sessionId": {"in": session_ids}}
            )

            # Calculate statistics
            total_corrections = len(corrections)
            grammar_count = sum(1 for c in corrections if c.correctionType == "grammar")
            pronunciation_count = sum(1 for c in corrections if c.correctionType == "pronunciation")
            vocabulary_count = sum(1 for c in corrections if c.correctionType == "vocabulary")

            severity_high = sum(1 for c in corrections if c.severity == "high")
            severity_medium = sum(1 for c in corrections if c.severity == "medium")
            severity_low = sum(1 for c in corrections if c.severity == "low")

            return {
                "total_corrections": total_corrections,
                "by_type": {
                    "grammar": grammar_count,
                    "pronunciation": pronunciation_count,
                    "vocabulary": vocabulary_count
                },
                "by_severity": {
                    "high": severity_high,
                    "medium": severity_medium,
                    "low": severity_low
                }
            }

        except Exception as e:
            print(f"Error getting correction stats: {e}")
            return {
                "total_corrections": 0,
                "by_type": {"grammar": 0, "pronunciation": 0, "vocabulary": 0},
                "by_severity": {"high": 0, "medium": 0, "low": 0}
            }

    def format_correction_feedback(self, analysis: Dict) -> str:
        """
        Format correction analysis into user-friendly feedback

        Args:
            analysis: Analysis result from LLM

        Returns:
            Formatted feedback string
        """
        if not analysis.get("has_errors"):
            return "Great! Your sentence is correct. " + (analysis.get("overall_feedback", ""))

        feedback_parts = []

        corrections = analysis.get("corrections", [])
        if corrections:
            feedback_parts.append("Here are some corrections:")
            for correction in corrections:
                feedback_parts.append(
                    f"- {correction['type'].capitalize()}: "
                    f"'{correction['original']}' → '{correction['corrected']}' "
                    f"({correction.get('explanation', '')})"
                )

        better_expression = analysis.get("better_expression")
        if better_expression:
            feedback_parts.append(f"\nA more natural way to say this: '{better_expression}'")

        feedback_parts.append(f"\n{analysis.get('overall_feedback', '')}")

        return "\n".join(feedback_parts)
