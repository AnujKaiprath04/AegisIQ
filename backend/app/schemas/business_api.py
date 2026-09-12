from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.rag_engine.types import RAGCitation
from app.assistant_service.types import BusinessRecommendationCard


class ToolInfoResponse(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    required_permissions: List[str] = []


class ToolExecuteRequestSchema(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolExecuteResponseSchema(BaseModel):
    tool_name: str
    status: str
    result: Dict[str, Any] = {}
    execution_time_ms: float


class UnifiedDecisionRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, max_length=4000)
    persona: Optional[str] = "CEO"
    session_id: Optional[str] = None
    enable_tools: Optional[bool] = True


class UnifiedDecisionResponseSchema(BaseModel):
    session_id: str
    persona: str
    response: str
    intent: str
    confidence_score: float
    latency_ms: float
    citations: List[RAGCitation] = []
    recommendations: List[BusinessRecommendationCard] = []
    executed_tools: List[ToolExecuteResponseSchema] = []


class PlatformManifestResponse(BaseModel):
    platform_name: str
    part_2_version: str
    status: str
    modules_completed: List[Dict[str, Any]] = []
    total_part2_modules: int
    completion_percentage: float
    compliance_readiness: List[str] = []
