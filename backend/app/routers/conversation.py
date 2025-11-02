from fastapi import APIRouter, HTTPException
from app.models import SessionCreate, SessionResponse
from app.database import get_db
from datetime import datetime
from typing import List

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    """Create a new learning session"""
    try:
        db = get_db()

        # Verify user exists
        user = await db.user.find_unique(
            where={"id": session.user_id}
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create session
        new_session = await db.session.create(
            data={
                "userId": session.user_id
            },
            include={
                "conversations": True,
                "corrections": True
            }
        )

        return new_session

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End a learning session"""
    try:
        db = get_db()

        # Get session
        session = await db.session.find_unique(
            where={"id": session_id}
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.endedAt:
            raise HTTPException(status_code=400, detail="Session already ended")

        # Calculate duration
        duration = int((datetime.now() - session.startedAt).total_seconds())

        # Update session
        updated_session = await db.session.update(
            where={"id": session_id},
            data={
                "endedAt": datetime.now(),
                "duration": duration
            }
        )

        # Update user progress
        await update_user_progress(session.userId, session_id)

        return updated_session

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details"""
    try:
        db = get_db()

        session = await db.session.find_unique(
            where={"id": session_id},
            include={
                "conversations": True,
                "corrections": True
            }
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return session

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")


@router.get("/sessions/{session_id}/conversations")
async def get_session_conversations(session_id: str):
    """Get all conversations in a session"""
    try:
        db = get_db()

        conversations = await db.conversation.find_many(
            where={"sessionId": session_id},
            order={"timestamp": "asc"}
        )

        return conversations

    except Exception as e:
        print(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/sessions/{session_id}/corrections")
async def get_session_corrections(session_id: str):
    """Get all corrections in a session"""
    try:
        db = get_db()

        corrections = await db.correction.find_many(
            where={"sessionId": session_id},
            order={"createdAt": "asc"}
        )

        return corrections

    except Exception as e:
        print(f"Error getting corrections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get corrections")


async def update_user_progress(user_id: str, session_id: str):
    """Update user's overall progress after session ends"""
    try:
        db = get_db()

        # Get session data
        session = await db.session.find_unique(
            where={"id": session_id},
            include={
                "corrections": True
            }
        )

        if not session:
            return

        # Get user progress
        progress = await db.progress.find_unique(
            where={"userId": user_id}
        )

        if not progress:
            # Create progress if doesn't exist
            progress = await db.progress.create(
                data={"userId": user_id}
            )

        # Calculate correction counts by type
        corrections = session.corrections
        grammar_count = sum(1 for c in corrections if c.correctionType == "grammar")
        pronunciation_count = sum(1 for c in corrections if c.correctionType == "pronunciation")
        vocabulary_count = sum(1 for c in corrections if c.correctionType == "vocabulary")

        # Update progress
        await db.progress.update(
            where={"userId": user_id},
            data={
                "totalSessions": progress.totalSessions + 1,
                "totalDuration": progress.totalDuration + (session.duration or 0),
                "totalCorrections": progress.totalCorrections + len(corrections),
                "lastSessionDate": datetime.now()
            }
        )

    except Exception as e:
        print(f"Error updating progress: {e}")
