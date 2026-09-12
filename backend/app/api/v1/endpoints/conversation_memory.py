from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation_memory import (
    AppendMessageRequest,
    ContextWindowResponse,
    CreateSessionRequest,
    MessageResponse,
    SessionDetailResponse,
    SummarizeSessionResponse,
)
from app.memory_service.manager import ConversationMemoryManager

router = APIRouter(prefix="/ai/memory", tags=["Part 2 - Module 9: Conversation Memory"])


@router.get("/sessions", response_model=List[SessionDetailResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
):
    """List all active conversation memory sessions for the authenticated user."""
    sessions = ConversationMemoryManager.list_sessions(user_id=current_user.id)
    return [SessionDetailResponse(**s.model_dump()) for s in sessions]


@router.post("/sessions", response_model=SessionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
):
    """Initialize a new conversation memory session."""
    session = ConversationMemoryManager.create_session(
        user_id=current_user.id,
        title=req.title,
        custom_id=req.custom_id,
    )
    return SessionDetailResponse(**session.model_dump())


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve full conversation history, message log, and rolling summary for a session."""
    session = ConversationMemoryManager.get_session(session_id)
    return SessionDetailResponse(**session.model_dump())


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def append_message(
    session_id: str,
    req: AppendMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """Append a user or assistant message to the session's episodic memory."""
    msg = ConversationMemoryManager.append_message(
        session_id=session_id,
        role=req.role,
        content=req.content,
        intent=req.intent,
    )
    return MessageResponse(**msg.model_dump())


@router.get("/sessions/{session_id}/context-window", response_model=ContextWindowResponse)
def get_context_window(
    session_id: str,
    window_size: int = Query(10, ge=1, le=50),
    max_tokens: int = Query(2048, ge=256, le=8192),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the token-optimized sliding-window context payload with rolling background summary."""
    window = ConversationMemoryManager.get_context_window(
        session_id=session_id,
        window_size=window_size,
        max_tokens=max_tokens,
    )
    return ContextWindowResponse(**window.model_dump())


@router.post("/sessions/{session_id}/summarize", response_model=SummarizeSessionResponse)
def summarize_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger automated rolling summarization of earlier dialogue history."""
    summary = ConversationMemoryManager.generate_summary(session_id)
    return SummarizeSessionResponse(session_id=session_id, rolling_summary=summary)


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a conversation memory session and purge stored message history."""
    success = ConversationMemoryManager.delete_session(session_id)
    return {"session_id": session_id, "deleted": success}
