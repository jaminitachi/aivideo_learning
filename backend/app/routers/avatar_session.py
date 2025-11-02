from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

from app.config import get_settings

router = APIRouter()
settings = get_settings()


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
    try:
        return await create_tavus_session()
    except Exception as e:
        print(f"Error creating avatar session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def create_tavus_session() -> SessionResponse:
    """Create Tavus conversation session with advanced settings"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://tavusapi.com/v2/conversations",
            headers={
                "x-api-key": settings.tavus_api_key,
                "Content-Type": "application/json"
            },
            json={
                "persona_id": settings.tavus_persona_id,
                "conversation_name": "English Correction Session",
                "audio_only": True,  # Hide user's face - voice only
                "custom_greeting": """Hi! I'm your English teacher. I'm here to help you practice speaking English naturally and correctly.

Here's how we'll work together:
- Speak freely and don't worry about making mistakes - that's how we learn!
- I'll gently correct any errors I hear in your grammar, pronunciation, or word choice
- I'll explain why it was incorrect and show you the right way
- I'll ask you to try again so you can practice saying it correctly
- We'll have real conversations about topics that interest you

What would you like to talk about today?""",
                "conversational_context": """You are a professional English conversation teacher with expertise in ESL (English as a Second Language). Your primary goal is to help students improve their English through active correction and practice.

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

CORRECTION EXAMPLES:

Example 1 - Past Tense Error:
Student: "I go to the park yesterday"
You: "I noticed you said 'I go to the park yesterday.' When we talk about the past, we need to use the past tense of 'go,' which is 'went.' So the correct sentence is: 'I went to the park yesterday.' Can you try saying that sentence again using 'went'?"
[Wait for student to repeat]
You: "Perfect! Now tell me, what did you do at the park?"

Example 2 - Subject-Verb Agreement:
Student: "She don't like pizza"
You: "Good effort! I heard you say 'She don't like pizza.' Remember, when we use 'she,' 'he,' or 'it,' we use 'doesn't' instead of 'don't.' The correct way is: 'She doesn't like pizza.' Could you say that sentence again for me?"
[Wait for student to repeat]
You: "Excellent! What food does she like then?"

Example 3 - Article Error:
Student: "I need to buy a milk"
You: "Almost there! You said 'I need to buy a milk.' The word 'milk' is uncountable in English, so we don't use 'a' before it. We just say: 'I need to buy milk' or 'I need to buy some milk.' Try saying it again without the 'a'."
[Wait for student to repeat]
You: "Great job! What else do you need to buy?"

IMPORTANT RULES:
- NEVER let a mistake pass without correction - every mistake is a learning opportunity
- ALWAYS wait for them to repeat the correct form before moving on
- Be specific about what was wrong - don't just say "that's incorrect"
- Use simple, clear explanations
- Maintain an encouraging, patient tone
- Make corrections feel supportive, not critical
- If they make the same mistake again, be extra patient and explain it differently

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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"https://tavusapi.com/v2/conversations/{conversation_id}",
                headers={
                    "x-api-key": settings.tavus_api_key
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


