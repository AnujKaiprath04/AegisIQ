from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.assistant_service.types import (
    BusinessRecommendationCard,
    PersonaProfile,
    PersonaType,
)
from app.rag_engine.types import RAGCitation


class AssistantChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=4000, description="Executive business question or instruction")
    persona: Optional[PersonaType] = PersonaType.CEO
    session_id: Optional[str] = None


class AssistantChatResponse(BaseModel):
    session_id: str
    persona: str
    response: str
    intent: str
    confidence_score: float
    latency_ms: float
    citations: List[RAGCitation] = []
    recommendations: List[BusinessRecommendationCard] = []


class KPIExplainRequest(BaseModel):
    kpi_name: str = Field(..., min_length=2, max_length=100)
    persona: Optional[PersonaType] = PersonaType.CFO


class KPIExplainResponse(BaseModel):
    kpi_name: str
    current_value: str
    target_value: str
    variance: str
    root_cause_analysis: str
    primary_drivers: List[str] = []
    recommended_actions: List[str] = []


class RecommendationRequest(BaseModel):
    topic: str = Field(default="General Strategy")
    persona: Optional[PersonaType] = PersonaType.CEO


class RecommendationResponse(BaseModel):
    topic: str
    persona: str
    recommendations: List[BusinessRecommendationCard] = []


class PersonaListResponse(BaseModel):
    active_default: str
    personas: List[PersonaProfile]
