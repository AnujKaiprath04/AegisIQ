from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.assistant import (
    AIConversationDetail,
    AIConversationSummary,
    AIQueryRequest,
    AIQueryResponse,
    ExecutivePromptResponse,
)
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["Module 7: AI Executive Assistant & NLQ"])


@router.post("/query", response_model=AIQueryResponse, status_code=status.HTTP_200_OK)
def query_ai_assistant(
    req: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute natural language enterprise decision query with multi-persona reasoning and SQL synthesis."""
    return AssistantService.generate_response(db=db, req=req, user=current_user)


@router.get("/conversations", response_model=List[AIConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List historical AI conversational decision threads for active user."""
    return AssistantService.get_conversations(db=db, user=current_user)


@router.get("/conversations/{conversation_id}", response_model=AIConversationDetail)
def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full message history, generated SQL queries, and recommendation cards for a conversation."""
    return AssistantService.get_conversation_detail(db=db, conversation_id=conversation_id, user=current_user)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove conversation thread and associated message history."""
    AssistantService.delete_conversation(db=db, conversation_id=conversation_id, user=current_user)
    return {"message": f"Conversation thread {conversation_id} successfully deleted."}


@router.get("/prompts", response_model=List[ExecutivePromptResponse])
def get_recommended_prompts(
    persona: Optional[str] = Query(None, description="CEO_STRATEGIST, CFO_FINANCIAL, CTO_ARCHITECT, BI_ANALYST, SECURITY_OFFICER"),
    current_user: User = Depends(get_current_user),
):
    """Retrieve tailored quick-action prompt chips for the active executive persona."""
    return AssistantService.get_prompt_templates(persona=persona)
