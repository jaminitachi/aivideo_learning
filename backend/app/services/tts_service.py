from elevenlabs import generate, Voice, VoiceSettings
from app.config import get_settings
from typing import Optional
import base64

settings = get_settings()


class TTSService:
    """Text-to-Speech service using ElevenLabs API"""

    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        # Default voice ID (you can customize this)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Optional[bytes]:
        """
        Generate speech from text using ElevenLabs

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (uses default if not provided)
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)

        Returns:
            Audio data as bytes or None if failed
        """
        try:
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id or self.default_voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost
                    )
                ),
                model="eleven_monolingual_v1",
                api_key=self.api_key
            )

            return audio

        except Exception as e:
            print(f"Error in TTS service: {e}")
            return None

    async def generate_speech_base64(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate speech and return as base64 string

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID

        Returns:
            Base64 encoded audio or None if failed
        """
        try:
            audio_bytes = await self.generate_speech(text, voice_id)
            if audio_bytes:
                return base64.b64encode(audio_bytes).decode('utf-8')
            return None

        except Exception as e:
            print(f"Error generating base64 audio: {e}")
            return None

    @staticmethod
    def get_available_voices() -> list:
        """
        Get list of available voices

        Returns:
            List of voice configurations
        """
        return [
            {
                "id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "description": "Young American female"
            },
            {
                "id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Domi",
                "description": "Young American female"
            },
            {
                "id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Sarah",
                "description": "Young American female"
            },
            {
                "id": "ErXwobaYiN019PkySvjV",
                "name": "Antoni",
                "description": "Young American male"
            },
            {
                "id": "VR6AewLTigWG4xSOukaG",
                "name": "Arnold",
                "description": "American male"
            }
        ]
