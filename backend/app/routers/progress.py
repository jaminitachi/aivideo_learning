from fastapi import APIRouter, HTTPException
from app.models import ProgressResponse
from app.database import get_db
from app.services.correction_service import CorrectionService

router = APIRouter()
correction_service = CorrectionService()


@router.get("/{user_id}", response_model=ProgressResponse)
async def get_user_progress(user_id: str):
    """Get user's learning progress"""
    try:
        db = get_db()

        progress = await db.progress.find_unique(
            where={"userId": user_id}
        )

        if not progress:
            # Create progress record if doesn't exist
            progress = await db.progress.create(
                data={"userId": user_id}
            )

        return progress

    except Exception as e:
        print(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress")


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get detailed statistics for user"""
    try:
        db = get_db()

        # Get progress
        progress = await db.progress.find_unique(
            where={"userId": user_id}
        )

        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")

        # Get correction stats
        correction_stats = await correction_service.get_correction_stats(user_id)

        # Get recent sessions
        recent_sessions = await db.session.find_many(
            where={"userId": user_id},
            order={"startedAt": "desc"},
            take=5,
            include={"corrections": True}
        )

        # Calculate average session duration
        avg_duration = 0
        if progress.totalSessions > 0:
            avg_duration = progress.totalDuration / progress.totalSessions

        return {
            "progress": progress,
            "correction_stats": correction_stats,
            "recent_sessions": recent_sessions,
            "average_session_duration": avg_duration,
            "total_conversations": await get_total_conversations(user_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@router.get("/{user_id}/weaknesses")
async def get_user_weaknesses(user_id: str):
    """Identify user's weak areas based on corrections"""
    try:
        db = get_db()

        # Get all corrections
        sessions = await db.session.find_many(
            where={"userId": user_id},
            select={"id": True}
        )

        session_ids = [s.id for s in sessions]

        corrections = await db.correction.find_many(
            where={"sessionId": {"in": session_ids}},
            order={"createdAt": "desc"}
        )

        # Analyze patterns
        grammar_errors = [c for c in corrections if c.correctionType == "grammar"]
        pronunciation_errors = [c for c in corrections if c.correctionType == "pronunciation"]
        vocabulary_errors = [c for c in corrections if c.correctionType == "vocabulary"]

        # Find most common mistakes
        common_grammar_mistakes = {}
        for correction in grammar_errors[:20]:  # Last 20 grammar errors
            key = correction.originalText.lower()
            common_grammar_mistakes[key] = common_grammar_mistakes.get(key, 0) + 1

        return {
            "weakness_areas": {
                "grammar": len(grammar_errors),
                "pronunciation": len(pronunciation_errors),
                "vocabulary": len(vocabulary_errors)
            },
            "common_mistakes": sorted(
                common_grammar_mistakes.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "recent_corrections": corrections[:10],
            "improvement_suggestions": generate_suggestions(corrections)
        }

    except Exception as e:
        print(f"Error analyzing weaknesses: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze weaknesses")


async def get_total_conversations(user_id: str) -> int:
    """Get total number of conversations for user"""
    try:
        db = get_db()

        sessions = await db.session.find_many(
            where={"userId": user_id},
            select={"id": True}
        )

        session_ids = [s.id for s in sessions]

        conversations = await db.conversation.find_many(
            where={"sessionId": {"in": session_ids}}
        )

        return len(conversations)

    except Exception as e:
        print(f"Error counting conversations: {e}")
        return 0


def generate_suggestions(corrections: list) -> list:
    """Generate improvement suggestions based on correction patterns"""
    suggestions = []

    grammar_count = sum(1 for c in corrections if c.correctionType == "grammar")
    pronunciation_count = sum(1 for c in corrections if c.correctionType == "pronunciation")
    vocabulary_count = sum(1 for c in corrections if c.correctionType == "vocabulary")

    total = len(corrections)

    if total == 0:
        return ["계속 연습하면서 실력을 키워보세요!"]

    if grammar_count / total > 0.5:
        suggestions.append("문법 규칙을 더 연습해보세요. 특히 시제와 전치사에 집중하세요.")

    if pronunciation_count / total > 0.3:
        suggestions.append("발음 연습이 필요합니다. 천천히 또박또박 말해보세요.")

    if vocabulary_count / total > 0.3:
        suggestions.append("어휘력 향상을 위해 새로운 표현을 더 배워보세요.")

    if not suggestions:
        suggestions.append("잘하고 있습니다! 계속 연습하세요.")

    return suggestions
