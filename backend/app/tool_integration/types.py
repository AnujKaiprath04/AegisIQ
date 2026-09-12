from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.rag_engine.types import RAGCitation
from app.assistant_service.types import BusinessRecommendationCard


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    required_permissions: List[str] = ["Viewer"]


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolExecutionResult(BaseModel):
    tool_name: str
    status: str
    result: Dict[str, Any] = {}
    execution_time_ms: float


class UnifiedDecisionRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=4000, description="Executive business or operational instruction")
    persona: Optional[str] = "CEO"
    session_id: Optional[str] = None
    enable_tools: bool = True


class UnifiedDecisionResponse(BaseModel):
    session_id: str
    persona: str
    response: str
    intent: str
    confidence_score: float
    latency_ms: float
    citations: List[RAGCitation] = []
    recommendations: List[BusinessRecommendationCard] = []
    executed_tools: List[ToolExecutionResult] = []
