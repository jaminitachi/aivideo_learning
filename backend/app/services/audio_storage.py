import os
import time
from pathlib import Path
from typing import Optional
from app.config import get_settings
import aiofiles

settings = get_settings()


class AudioStorage:
    """Service for storing and managing audio files locally"""

    def __init__(self):
        # Static audio directory
        self.audio_dir = Path("static/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        # Base URL for serving audio files
        self.base_url = "http://localhost:8000/static/audio"

    async def save_audio(self, audio_bytes: bytes, session_id: str) -> str:
        """
        Save audio bytes to a local file and return public URL

        Args:
            audio_bytes: Audio data in bytes
            session_id: Session identifier

        Returns:
            Public URL to access the audio file
        """
        try:
            # Generate filename with timestamp
            timestamp = int(time.time() * 1000)
            filename = f"{session_id}_{timestamp}.mp3"
            filepath = self.audio_dir / filename

            # Save audio file asynchronously
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(audio_bytes)

            # Return public URL
            public_url = f"{self.base_url}/{filename}"
            print(f"Audio saved: {public_url}")
            return public_url

        except Exception as e:
            print(f"Error saving audio: {e}")
            return None

    async def cleanup_old_files(self, hours: int = 24):
        """
        Delete audio files older than specified hours

        Args:
            hours: Age threshold in hours (default: 24)
        """
        try:
            current_time = time.time()
            threshold = hours * 3600  # Convert to seconds

            for filepath in self.audio_dir.glob("*.mp3"):
                # Check file modification time
                file_age = current_time - filepath.stat().st_mtime

                if file_age > threshold:
                    filepath.unlink()
                    print(f"Deleted old audio file: {filepath.name}")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    def get_file_count(self) -> int:
        """
        Get the number of audio files currently stored

        Returns:
            Number of .mp3 files
        """
        return len(list(self.audio_dir.glob("*.mp3")))

    def get_total_size_mb(self) -> float:
        """
        Get total size of all audio files in MB

        Returns:
            Total size in megabytes
        """
        total_bytes = sum(f.stat().st_size for f in self.audio_dir.glob("*.mp3"))
        return total_bytes / (1024 * 1024)
