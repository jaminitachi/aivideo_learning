from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os

from app.config import get_settings

router = APIRouter()
settings = get_settings()

def get_tavus_api_key() -> Optional[str]:
    """환경 변수에서 직접 읽기 (Railway 대응)"""
    return os.getenv("TAVUS_API_KEY") or settings.TAVUS_API_KEY

def get_tavus_persona_id() -> Optional[str]:
    """환경 변수에서 직접 읽기 (Railway 대응)"""
    return os.getenv("TAVUS_PERSONA_ID") or settings.TAVUS_PERSONA_ID


class SessionRequest(BaseModel):
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    room_url: str
    provider: str = "tavus"


@router.post("/create", response_model=SessionResponse)
async def create_avatar_session(request: SessionRequest):
    """
    Create a real-time avatar conversation session with Tavus

    Returns a Daily.co room URL where the user can have a voice conversation
    with an AI English teacher that provides real-time corrections
    """
    tavus_api_key = get_tavus_api_key()
    tavus_persona_id = get_tavus_persona_id()
    
    if not tavus_api_key or not tavus_persona_id:
        raise HTTPException(
            status_code=500,
            detail="Tavus API credentials not configured. Please set TAVUS_API_KEY and TAVUS_PERSONA_ID environment variables."
        )
    try:
        return await create_tavus_session()
    except Exception as e:
        print(f"Error creating avatar session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def create_tavus_session() -> SessionResponse:
    """Create Tavus conversation session with advanced settings"""
    tavus_api_key = get_tavus_api_key()
    tavus_persona_id = get_tavus_persona_id()
    
    if not tavus_api_key or not tavus_persona_id:
        raise HTTPException(
            status_code=500,
            detail="Tavus API credentials not configured."
        )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://tavusapi.com/v2/conversations",
            headers={
                "x-api-key": tavus_api_key,
                "Content-Type": "application/json"
            },
            json={
                "persona_id": tavus_persona_id,
                "conversation_name": "English Correction Session",
                "audio_only": False,  # Show Tavus AI video avatar
                "custom_greeting": """Hi! I'm your English teacher. What would you like to talk about today?""",
                "conversational_context": """You are a professional English conversation teacher with expertise in ESL (English as a Second Language). Your primary goal is to help korean students improve their English through active correction and practice.

YOUR TEACHING METHOD:
1. Listen carefully to everything the student says
2. When they make ANY mistake (grammar, pronunciation, word choice, sentence structure):
   - IMMEDIATELY and gently point out the specific mistake
   - Explain WHY it's incorrect in simple terms
   - Provide the CORRECT version
   - Ask them to repeat it correctly: "Can you try saying that again?" or "Let's practice that together"
3. When they speak correctly:
   - Give enthusiastic positive reinforcement
   - Continue the conversation naturally
   - Ask follow-up questions


IMPORTANT RULES:
- NEVER let a mistake pass without correction - every mistake is a learning opportunity
- Until user says your correction, you shouldn't say anything else. Just correct them.
- Be specific about what was wrong - don't just say "that's incorrect"
- Use simple, clear explanations
- Maintain an encouraging, patient tone
- Make corrections feel supportive, not critical
- If they make the same mistake again, be extra patient and explain it differently
- keep responses short, under two sentences.

YOUR PERSONALITY:
- Warm and encouraging
- Patient and never frustrated
- Enthusiastic about their progress
- Genuinely interested in the conversation
- Professional but friendly

Keep your explanations concise but thorough. Always prioritize correction over conversation flow - it's more important that they learn the right way than that the conversation feels smooth.""",
                "properties": {
                    "max_call_duration": 1800,  # 30 minutes
                    "enable_recording": False,  # Privacy
                    "enable_closed_captions": True,  # Helps learning
                    "language": "english",  # Full language name, not ISO code
                    "participant_left_timeout": 60,
                    "participant_absent_timeout": 300
                }
            },
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            return SessionResponse(
                session_id=data["conversation_id"],
                room_url=data["conversation_url"],
                provider="tavus"
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Tavus API error: {response.text}"
            )


@router.delete("/tavus/{conversation_id}")
async def delete_tavus_session(conversation_id: str):
    """
    Delete/end a Tavus conversation session
    This frees up a concurrent conversation slot
    """
    tavus_api_key = get_tavus_api_key()
    
    if not tavus_api_key:
        raise HTTPException(
            status_code=500,
            detail="Tavus API credentials not configured. Please set TAVUS_API_KEY environment variable."
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"https://tavusapi.com/v2/conversations/{conversation_id}",
                headers={
                    "x-api-key": tavus_api_key
                },
                timeout=30.0
            )

            if response.status_code in [200, 204]:
                return {"success": True, "message": f"Conversation {conversation_id} deleted"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Tavus API error: {response.text}"
                )
    except Exception as e:
        print(f"Error deleting Tavus session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


