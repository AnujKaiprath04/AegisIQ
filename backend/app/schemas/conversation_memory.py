from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.memory_service.types import ChatMessageRecord


class CreateSessionRequest(BaseModel):
    title: Optional[str] = Field(default="Executive Decision Session")
    custom_id: Optional[str] = None


class AppendMessageRequest(BaseModel):
    role: str = Field(default="user", description="user, assistant, or system")
    content: str = Field(..., min_length=1, max_length=10000)
    intent: Optional[str] = None


class MessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    tokens: int
    timestamp: str
    intent: Optional[str] = None


class SessionDetailResponse(BaseModel):
    session_id: str
    user_id: int
    title: str
    created_at: str
    updated_at: str
    total_messages: int
    total_tokens: int
    rolling_summary: Optional[str] = None
    messages: List[MessageResponse] = []


class ContextWindowResponse(BaseModel):
    session_id: str
    rolling_summary: Optional[str] = None
    recent_messages: List[MessageResponse] = []
    total_context_tokens: int


class SummarizeSessionResponse(BaseModel):
    session_id: str
    rolling_summary: str
