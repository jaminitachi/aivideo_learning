from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Tavus (Real-time AI English Teacher)
    TAVUS_API_KEY: str
    TAVUS_PERSONA_ID: str

    # JWT (optional - for future authentication)
    SECRET_KEY: str = "temp_secret_key_not_used"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
