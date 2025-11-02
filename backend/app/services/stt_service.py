import httpx
from app.config import get_settings
import io
from typing import Optional

settings = get_settings()


class STTService:
    """Speech-to-Text service using ElevenLabs Scribe v1 (94% accuracy)"""

    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"

    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio data to text using ElevenLabs Scribe API

        Args:
            audio_data: Audio file bytes
            language: Language code (default: "en")

        Returns:
            Transcribed text or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {
                    'audio': ('audio.webm', audio_data, 'audio/webm')
                }

                headers = {
                    "xi-api-key": self.api_key
                }
                
                data = {
                    "model_id": "eleven_multilingual_v2"
                }

                # ElevenLabs Scribe API endpoint
                response = await client.post(
                    f"{self.base_url}/speech-to-text",
                    files=files,
                    headers=headers,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    # Extract text from response
                    return result.get("text", "")
                else:
                    print(f"ElevenLabs STT error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"Error in STT service: {e}")
            return None

    async def transcribe_with_metadata(self, audio_data: bytes, language: str = "en") -> Optional[dict]:
        """
        Transcribe audio with full metadata (speaker info, timestamps, etc.)

        Args:
            audio_data: Audio file bytes
            language: Language code (default: "en")

        Returns:
            Dictionary with full transcription metadata or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {
                    'audio': ('audio.webm', audio_data, 'audio/webm')
                }

                headers = {
                    "xi-api-key": self.api_key
                }

                # Optional: Enable speaker diarization
                data = {
                    "model": "scribe-v1",
                    "language": language
                }

                response = await client.post(
                    f"{self.base_url}/speech-to-text",
                    files=files,
                    headers=headers,
                    data=data
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"ElevenLabs STT error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"Error in STT service with metadata: {e}")
            return None
