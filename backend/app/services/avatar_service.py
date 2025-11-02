import httpx
from app.config import get_settings
from typing import Optional, Dict
import asyncio

settings = get_settings()


class AvatarService:
    """Video Avatar service using D-ID API"""

    def __init__(self):
        self.api_key = settings.did_api_key
        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default presenter (you can customize this)
        self.default_presenter = "amy-jcwCkr1grs"

    async def create_talk(
        self,
        script_text: str,
        presenter_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a talking video using D-ID API with text script and ElevenLabs TTS
        Args:
            script_text: The text the avatar will speak
            presenter_id: D-ID presenter ID
        Returns:
            Dictionary with video creation details or None if failed
        """
        try:
            # Add ElevenLabs API key to headers
            headers = self.headers.copy()
            headers["x-api-key-external"] = f'{{"elevenlabs": "{settings.elevenlabs_api_key}"}}'

            async with httpx.AsyncClient() as client:
                payload = {
                    "script": {
                        "type": "text",
                        "input": script_text,
                        "provider": {
                            "type": "elevenlabs",
                            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                            "voice_config": {
                                "stability": 0.5,
                                "similarity_boost": 0.75,
                                "model_id": "eleven_multilingual_v2"
                            }
                        }
                    },
                    "config": {
                        "fluent": False,  # Boolean, not string
                        "pad_audio": 0.0  # Number, not string
                    },
                    "source_url": f"https://create-images-results.d-id.com/DefaultPresenters/{presenter_id or self.default_presenter}/image.jpeg"
                }

                response = await client.post(
                    f"{self.base_url}/talks",
                    headers=headers,  # Use updated headers with ElevenLabs API key
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 201:
                    result = response.json()
                    print(f"D-ID talk created successfully: {result.get('id')}")
                    return result
                else:
                    print(f"D-ID API error: {response.status_code}")
                    print(f"Response headers: {response.headers}")
                    print(f"Response body: {response.text}")
                    print(f"Request payload: {payload}")
                    print(f"Request headers: {headers}")
                    return None

        except Exception as e:
            import traceback
            print(f"Error creating talk: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None

    async def get_talk_status(self, talk_id: str) -> Optional[Dict]:
        """
        Get the status of a talk video

        Args:
            talk_id: D-ID talk ID

        Returns:
            Dictionary with talk status or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error getting talk status: {response.status_code}")
                    return None

        except Exception as e:
            print(f"Error getting talk status: {e}")
            return None

    async def wait_for_talk_completion(
        self,
        talk_id: str,
        max_wait_time: int = 60,
        poll_interval: int = 2
    ) -> Optional[str]:
        """
        Wait for talk video to be ready and return the video URL

        Args:
            talk_id: D-ID talk ID
            max_wait_time: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds

        Returns:
            Video URL or None if failed/timeout
        """
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            status = await self.get_talk_status(talk_id)

            if status:
                if status.get("status") == "done":
                    return status.get("result_url")
                elif status.get("status") == "error":
                    print(f"Talk creation failed: {status.get('error')}")
                    return None

            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval

        print("Timeout waiting for talk completion")
        return None


    @staticmethod
    def get_available_presenters() -> list:
        """
        Get list of available presenters

        Returns:
            List of presenter configurations
        """
        return [
            {
                "id": "amy-jcwCkr1grs",
                "name": "Amy",
                "description": "Young professional female"
            },
            {
                "id": "anna-Uw4aHbjzqK",
                "name": "Anna",
                "description": "Friendly female presenter"
            },
            {
                "id": "eric-V8L7PaFHWv",
                "name": "Eric",
                "description": "Professional male presenter"
            }
        ]
