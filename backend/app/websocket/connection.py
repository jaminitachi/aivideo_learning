from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.services.avatar_service import AvatarService
from app.services.correction_service import CorrectionService
from app.services.audio_storage import AudioStorage
from app.database import get_db
import base64

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_histories: Dict[str, List[Dict]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.conversation_histories[session_id] = []
        print(f"Client connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.conversation_histories:
            del self.conversation_histories[session_id]
        print(f"Client disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        return self.conversation_histories.get(session_id, [])

    def add_to_history(self, session_id: str, role: str, content: str):
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
        self.conversation_histories[session_id].append({
            "role": role,
            "content": content
        })


manager = ConnectionManager()
stt_service = STTService()
llm_service = LLMService()
tts_service = TTSService()
avatar_service = AvatarService()
correction_service = CorrectionService()
audio_storage = AudioStorage()


@router.websocket("/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time conversation

    Message format:
    {
        "type": "audio" | "text" | "control",
        "data": {
            "audio": base64_encoded_audio,  // for type: audio
            "text": "user text",            // for type: text
            "command": "start" | "stop"     // for type: control
        }
    }
    """
    await manager.connect(websocket, session_id)

    try:
        # Send welcome message
        try:
            welcome = await llm_service.generate_conversation_starter("beginner")
            manager.add_to_history(session_id, "assistant", welcome)

            # Generate welcome audio and video with ElevenLabs + D-ID
            audio_bytes = await tts_service.generate_speech(welcome)
            audio_base64 = None
            video_url = None

            if audio_bytes:
                # Save audio to local storage and get public URL
                audio_url = await audio_storage.save_audio(audio_bytes, session_id)

                # Convert to base64 for frontend playback
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

                # Create avatar video with D-ID
                try:
                    talk_result = await avatar_service.create_talk(welcome)
                    if talk_result:
                        talk_id = talk_result.get("id")
                        video_url = await avatar_service.wait_for_talk_completion(talk_id, max_wait_time=30)
                except Exception as video_error:
                    print(f"Welcome video generation failed (continuing without video): {video_error}")

            await manager.send_message(session_id, {
                "type": "response",
                "data": {
                    "text": welcome,
                    "audio": audio_base64,
                    "video_url": video_url
                }
            })
        except Exception as welcome_error:
            print(f"Welcome message generation failed: {welcome_error}")
            # Send a simple fallback welcome message
            await manager.send_message(session_id, {
                "type": "response",
                "data": {
                    "text": "Hello! I'm ready to help you practice English. Please start speaking!",
                    "audio": None,
                    "video_url": None
                }
            })

        while True:
            # Receive message from client
            message = await websocket.receive_json()
            message_type = message.get("type")
            data = message.get("data", {})

            if message_type == "control":
                command = data.get("command")
                if command == "stop":
                    break

            elif message_type == "audio":
                # Process audio input with ElevenLabs STT
                audio_base64_data = data.get("audio")
                if audio_base64_data:
                    audio_bytes = base64.b64decode(audio_base64_data)

                    # Transcribe audio to text using ElevenLabs Scribe (94% accuracy)
                    user_text = await stt_service.transcribe_audio(audio_bytes)

                    if user_text:
                        await process_user_input(session_id, user_text)
                    else:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "data": {"message": "음성 인식에 실패했습니다. 다시 말씀해주세요."}
                        })

            elif message_type == "text":
                # Process text input
                user_text = data.get("text")
                if user_text:
                    await process_user_input(session_id, user_text)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)


async def process_user_input(session_id: str, user_text: str):
    """Process user input and generate response"""

    try:
        # Send acknowledgment
        await manager.send_message(session_id, {
            "type": "transcription",
            "data": {"text": user_text}
        })

        # Analyze for corrections
        analysis = await correction_service.analyze_text(user_text)

        # Send correction feedback if there are errors
        if analysis.get("has_errors"):
            feedback = correction_service.format_correction_feedback(analysis)
            await manager.send_message(session_id, {
                "type": "correction",
                "data": {
                    "has_errors": True,
                    "corrections": analysis.get("corrections", []),
                    "better_expression": analysis.get("better_expression"),
                    "feedback": feedback
                }
            })

            # Save corrections to database
            db = get_db()
            conversation = await db.conversation.create(
                data={
                    "sessionId": session_id,
                    "role": "user",
                    "content": user_text
                }
            )

            if analysis.get("corrections"):
                await correction_service.save_corrections(
                    session_id,
                    conversation.id,
                    analysis.get("corrections", [])
                )

        # Add to conversation history
        manager.add_to_history(session_id, "user", user_text)

        # Generate response using GPT-5
        conversation_history = manager.get_conversation_history(session_id)
        response_text = await llm_service.generate_response(user_text, conversation_history)

        manager.add_to_history(session_id, "assistant", response_text)

        # Generate audio with ElevenLabs TTS
        audio_bytes = await tts_service.generate_speech(response_text)
        audio_base64 = None
        audio_url = None

        if audio_bytes:
            # Save audio to local storage (needed for history, not for D-ID anymore)
            audio_url = await audio_storage.save_audio(audio_bytes, session_id)
            # Convert to base64 for frontend playback
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # Send initial response with text & audio immediately
        await manager.send_message(session_id, {
            "type": "response",
            "data": {
                "text": response_text,
                "audio": audio_base64,
                "video_url": None # Video will be sent in a separate message later
            }
        })
        
        # Now, start the video generation in the background
        try:
            talk_result = await avatar_service.create_talk(response_text)
            if talk_result:
                talk_id = talk_result.get("id")
                asyncio.create_task(
                    wait_and_send_video(session_id, talk_id, response_text)
                )
        except Exception as video_error:
            print(f"Video generation task could not be started: {video_error}")


        # Save conversation to database
        db = get_db()
        await db.conversation.create(
            data={
                "sessionId": session_id,
                "role": "assistant",
                "content": response_text,
                "audioUrl": audio_url,
                "videoUrl": None  # Video URL will be updated when available
            }
        )

    except Exception as e:
        print(f"Error processing user input: {e}")
        await manager.send_message(session_id, {
            "type": "error",
            "data": {"message": "처리 중 오류가 발생했습니다."}
        })


async def wait_and_send_video(session_id: str, talk_id: str, text: str):
    """Wait for video generation and send when ready"""
    video_url = await avatar_service.wait_for_talk_completion(talk_id, max_wait_time=60)

    if video_url:
        # Send a new message ONLY containing the final video URL and context
        await manager.send_message(session_id, {
            "type": "video_update",
            "data": {
                "text": text,
                "video_url": video_url
            }
        })

        # Also update the database record with the new video URL
        db = get_db()
        # Find the corresponding conversation and update it
        await db.conversation.update_many(
            where={
                "sessionId": session_id,
                "content": text,
            },
            data={'videoUrl': video_url}
        )
