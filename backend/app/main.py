from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import connect_db, disconnect_db
from app.routers import conversation, user, progress, avatar_session

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()


app = FastAPI(
    title="VideoEngAI API",
    description="AI Video Avatar English Learning Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(conversation.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(avatar_session.router, prefix="/api/avatar-sessions", tags=["Avatar Sessions"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to VideoEngAI API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
    
@app.get("/debug/env")
async def check_env():
    """환경 변수 설정 상태 확인 (디버그용)"""
    import os
    return {
        "tavus_api_key_from_settings": bool(settings.TAVUS_API_KEY),
        "tavus_persona_id_from_settings": bool(settings.TAVUS_PERSONA_ID),
        "tavus_api_key_from_os": bool(os.getenv("TAVUS_API_KEY")),
        "tavus_persona_id_from_os": bool(os.getenv("TAVUS_PERSONA_ID")),
        "all_env_vars_with_tavus": [k for k in os.environ.keys() if "TAVUS" in k.upper()]
    }