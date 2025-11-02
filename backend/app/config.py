from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # OpenRouter (for GPT-5-chat)
    openrouter_api_key: str
    site_url: str = "http://localhost:3000"
    site_name: str = "VideoEngAI"

    # ElevenLabs (STT + TTS)
    elevenlabs_api_key: str

    # D-ID (Video Avatar)
    did_api_key: str

    # Tavus (Video Avatar - English Teacher)
    tavus_api_key: str
    tavus_persona_id: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
