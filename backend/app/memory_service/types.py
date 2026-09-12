from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessageRecord(BaseModel):
    message_id: str
    role: str = Field(..., description="user, assistant, or system")
    content: str
    tokens: int
    timestamp: str
    intent: Optional[str] = None


class SessionMemoryState(BaseModel):
    session_id: str
    user_id: int
    title: str
    created_at: str
    updated_at: str
    total_messages: int
    total_tokens: int
    rolling_summary: Optional[str] = None
    messages: List[ChatMessageRecord] = []


class ContextWindowPayload(BaseModel):
    session_id: str
    rolling_summary: Optional[str] = None
    recent_messages: List[ChatMessageRecord] = []
    total_context_tokens: int
