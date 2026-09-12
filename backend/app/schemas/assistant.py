from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Executive natural language question")
    persona: str = Field("CEO_STRATEGIST", description="CEO_STRATEGIST, CFO_FINANCIAL, CTO_ARCHITECT, BI_ANALYST, SECURITY_OFFICER")
    conversation_id: Optional[int] = None
    dataset_id: Optional[int] = None
    include_sql_synthesis: bool = True


class AIMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    generated_sql: Optional[str] = None
    data_results: Optional[List[Dict[str, Any]]] = []
    citations: List[str] = []
    recommendations: List[str] = []
    tokens_used: int = 0
    latency_ms: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class AIQueryResponse(BaseModel):
    conversation_id: int
    message: AIMessageResponse


class AIConversationSummary(BaseModel):
    id: int
    title: str
    persona: str
    messages_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIConversationDetail(BaseModel):
    id: int
    title: str
    persona: str
    messages: List[AIMessageResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutivePromptResponse(BaseModel):
    id: str
    persona: str
    title: str
    prompt_text: str
    category: str
