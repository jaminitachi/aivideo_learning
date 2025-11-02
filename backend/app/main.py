from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.database import connect_db, disconnect_db
from app.routers import conversation, user, progress, avatar_session
from app.websocket.connection import router as websocket_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create static directory for audio files
    os.makedirs("static/audio", exist_ok=True)
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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket_router, tags=["WebSocket"])
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
