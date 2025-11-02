from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    email: str
    name: str
    created_at: datetime = Field(alias="createdAt")


class ConversationCreate(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    audio_url: Optional[str] = None
    video_url: Optional[str] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    session_id: str = Field(alias="sessionId")
    role: str
    content: str
    audio_url: Optional[str] = Field(alias="audioUrl")
    video_url: Optional[str] = Field(alias="videoUrl")
    timestamp: datetime


class CorrectionCreate(BaseModel):
    correction_type: str  # "grammar", "pronunciation", "vocabulary"
    original_text: str
    corrected_text: str
    explanation: Optional[str] = None
    severity: str = "medium"


class CorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    correction_type: str = Field(alias="correctionType")
    original_text: str = Field(alias="originalText")
    corrected_text: str = Field(alias="correctedText")
    explanation: Optional[str]
    severity: str
    created_at: datetime = Field(alias="createdAt")


class SessionCreate(BaseModel):
    user_id: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    started_at: datetime = Field(alias="startedAt")
    ended_at: Optional[datetime] = Field(alias="endedAt", default=None)
    duration: Optional[int] = None
    conversations: List[ConversationResponse] = []
    corrections: List[CorrectionResponse] = []


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    total_sessions: int = Field(alias="totalSessions")
    total_duration: int = Field(alias="totalDuration")
    total_corrections: int = Field(alias="totalCorrections")
    grammar_score: float = Field(alias="grammarScore")
    pronunciation_score: float = Field(alias="pronunciationScore")
    vocabulary_score: float = Field(alias="vocabularyScore")
    last_session_date: Optional[datetime] = Field(alias="lastSessionDate", default=None)


class WebSocketMessage(BaseModel):
    type: str  # "audio", "text", "control"
    data: dict
