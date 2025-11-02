# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoEngAI is an AI video avatar-powered English learning platform. Users have real-time conversations with AI avatars that provide immediate corrections for grammar, pronunciation, and vocabulary. The platform supports both asynchronous conversations (D-ID video avatars) and real-time voice conversations (Tavus avatars).

## Development Commands

### Backend (FastAPI)
```bash
cd backend

# Local development
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
prisma generate
prisma migrate dev
uvicorn app.main:app --reload

# Database operations
prisma migrate dev --name <migration_name>  # Create new migration
prisma studio  # Open database GUI at http://localhost:5555
prisma db push  # Push schema changes without migration
```

### Frontend (Next.js)
```bash
cd frontend

npm install
npm run dev    # Development server
npm run build  # Production build
npm run start  # Production server
npm run lint   # Lint check
```

### Docker
```bash
# Full stack
docker-compose up -d           # Start all services
docker-compose down           # Stop all services
docker-compose logs -f        # View logs
docker-compose exec backend prisma migrate dev  # Run migrations in container

# Individual services
docker-compose up backend     # Backend only
docker-compose up frontend    # Frontend only
```

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11+) with WebSocket support
- **Frontend**: Next.js 14 (App Router) with TypeScript
- **Database**: PostgreSQL 16 with Prisma ORM
- **AI Services**:
  - OpenRouter (GPT-5-chat for conversation)
  - ElevenLabs (STT via Scribe, TTS for voice)
  - D-ID (async video avatars)
  - Tavus (real-time conversational avatars)

### Real-Time Communication Flow

The platform has two conversation modes:

**1. Asynchronous Mode (WebSocket + D-ID):**
```
User audio → WebSocket (/conversation/{session_id})
  → ElevenLabs Scribe STT → GPT-5 analysis/response
  → ElevenLabs TTS → D-ID video generation (background task)
  → Response sent immediately (text + audio), video follows when ready
```

**2. Real-time Mode (Tavus):**
```
User → Tavus API creates Daily.co room
  → User joins video call with AI avatar
  → Avatar listens, corrects, and teaches in real-time
  → All conversation handled by Tavus (no WebSocket needed)
```

### Service Layer (backend/app/services/)

Key services that interact with external APIs:

- **stt_service.py**: ElevenLabs Scribe for 94% accuracy speech-to-text
- **llm_service.py**: OpenRouter GPT-5-chat for conversation generation and grammar analysis
- **tts_service.py**: ElevenLabs for natural-sounding speech synthesis
- **avatar_service.py**: D-ID for asynchronous video avatar generation
- **correction_service.py**: Analyzes text for grammar/pronunciation/vocabulary errors
- **audio_storage.py**: Manages local audio file storage in `backend/static/audio/`

### WebSocket Message Protocol

Messages to `/ws/conversation/{session_id}`:

**Client → Server:**
```json
{
  "type": "audio",
  "data": { "audio": "<base64_encoded_audio>" }
}
{
  "type": "text",
  "data": { "text": "user message" }
}
{
  "type": "control",
  "data": { "command": "stop" }
}
```

**Server → Client:**
```json
{
  "type": "transcription",
  "data": { "text": "transcribed text" }
}
{
  "type": "correction",
  "data": {
    "has_errors": true,
    "corrections": [...],
    "better_expression": "...",
    "feedback": "..."
  }
}
{
  "type": "response",
  "data": {
    "text": "AI response",
    "audio": "<base64>",
    "video_url": null  // Initially null
  }
}
{
  "type": "video_update",
  "data": {
    "text": "same text as before",
    "video_url": "https://..."  // D-ID video URL when ready
  }
}
```

### Database Schema (Prisma)

Core models in `backend/prisma/schema.prisma`:

- **User**: Basic user info (id, email, name, passwordHash)
- **Session**: Learning sessions linking to user
- **Conversation**: Individual messages (role, content, audioUrl, videoUrl)
- **Correction**: Error corrections (correctionType, originalText, correctedText, explanation, severity)
- **Progress**: Aggregated user progress and scores
- **PracticePhrase**: Pre-loaded practice content by category/difficulty

All foreign keys use cascade deletes. Session and conversation IDs are UUIDs.

### Configuration (backend/app/config.py)

Environment variables required:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY`: For GPT-5-chat access
- `ELEVENLABS_API_KEY`: For STT/TTS
- `DID_API_KEY`: For async video avatars
- `TAVUS_API_KEY`: For real-time avatar sessions
- `TAVUS_PERSONA_ID`: Specific Tavus persona to use
- `SECRET_KEY`: JWT secret
- `FRONTEND_URL`: CORS origin
- `SITE_URL`, `SITE_NAME`: OpenRouter metadata

### API Routes

**REST Endpoints:**
- `/api/users/*` - User management
- `/api/conversations/sessions/*` - Session CRUD operations
- `/api/progress/{user_id}/*` - Progress tracking and statistics
- `/api/avatar-sessions/create` - Create Tavus real-time avatar session
- `/api/avatar-sessions/tavus/{conversation_id}` - Delete Tavus session

**WebSocket:**
- `/ws/conversation/{session_id}` - Real-time bidirectional conversation

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Structure

- **src/app/**: Next.js App Router pages
  - `page.tsx`: Home page
  - `learning/[sessionId]/page.tsx`: Learning session page
- **src/components/**: React components
  - `VideoPlayer.tsx`: D-ID video playback
  - `ChatInterface.tsx`: Message display
  - `CorrectionFeedback.tsx`: Error feedback UI
  - `RepeatPractice.tsx`: Practice repetition
- **src/lib/**: Utilities
  - `websocket.ts`: WebSocket connection manager
  - `audioRecorder.ts`: Browser audio recording
- **src/types/index.ts**: TypeScript type definitions

State management uses Zustand. Styling with Tailwind CSS.

## Development Guidelines

### Adding New API Endpoints

1. Create router in `backend/app/routers/`
2. Define Pydantic models for request/response
3. Add router to `backend/app/main.py`
4. Use dependency injection for database (`get_db()`)

### Modifying Database Schema

1. Edit `backend/prisma/schema.prisma`
2. Run `prisma migrate dev --name descriptive_name`
3. Prisma client auto-regenerates
4. Update corresponding Pydantic models

### Working with AI Services

All service classes are singletons initialized in `websocket/connection.py`. They handle:
- API authentication via settings
- Error handling and retries
- Async operations with httpx/openai clients

When modifying AI integrations, maintain the existing pattern of returning `None` on errors and logging exceptions.

### WebSocket Development

The `ConnectionManager` in `websocket/connection.py` maintains:
- Active connections per session_id
- Conversation history per session
- Message routing

When adding message types, update both the sender and all receivers. Video generation runs in background tasks (`asyncio.create_task`) to avoid blocking responses.

### Frontend WebSocket Integration

The `websocket.ts` lib manages connection lifecycle, automatic reconnection, and message type routing. When adding message types on backend, add corresponding handlers in frontend components.

## Testing

Currently no automated tests are implemented. When adding tests:

**Backend:**
```bash
pip install pytest pytest-asyncio httpx
pytest
```

**Frontend:**
```bash
npm test  # Jest + React Testing Library
```

## Common Issues

### WebSocket Connection Failures
- Check CORS settings in `backend/app/main.py`
- Verify WebSocket URL uses `ws://` not `http://`
- Ensure backend is running before frontend connects

### Audio Recording Issues
- Requires HTTPS in production (localhost works in dev)
- Browser must grant microphone permissions
- Audio format must be supported by ElevenLabs Scribe

### Database Connection Errors
- Verify PostgreSQL is running (`docker-compose ps`)
- Check DATABASE_URL format in `.env`
- Ensure migrations are up to date (`prisma migrate dev`)

### D-ID Video Generation Timeouts
- Videos can take 30-60 seconds to generate
- Frontend receives response immediately, video updates later
- Check D-ID API quota and rate limits

### Tavus Session Issues
- Verify TAVUS_API_KEY and TAVUS_PERSONA_ID are set
- Check concurrent session limits on Tavus account
- Use DELETE endpoint to free up slots when done

## Deployment Notes

- Static audio files stored in `backend/static/audio/` (not persisted in Docker by default)
- Consider external storage (S3) for production audio/video
- WebSocket requires sticky sessions in load-balanced environments
- Prisma migrations run separately from app startup
- Environment variables passed via docker-compose or hosting platform
