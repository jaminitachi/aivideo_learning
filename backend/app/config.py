from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import os


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
        # 프로덕션(Railway)에서는 .env 파일 읽지 않음 - Railway Variables만 사용
        # 로컬 개발 시에만 .env 파일 사용
        env_file=".env" if os.path.exists(".env") and not os.getenv("RAILWAY_ENVIRONMENT") else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Railway에서 환경 변수가 주입되지 않는 경우를 위한 fallback
        if not self.TAVUS_API_KEY:
            self.TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")
        if not self.TAVUS_PERSONA_ID:
            self.TAVUS_PERSONA_ID = os.getenv("TAVUS_PERSONA_ID")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
