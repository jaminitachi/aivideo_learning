from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Tavus (Real-time AI English Teacher)
    TAVUS_API_KEY: Optional[str] = None
    TAVUS_PERSONA_ID: Optional[str] = None

    # JWT (optional - for future authentication)
    SECRET_KEY: str = "temp_secret_key_not_used"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",  # 로컬 개발용 (있으면 읽고, 없으면 환경 변수 사용)
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
