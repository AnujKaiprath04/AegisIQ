from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.rag_engine.types import RAGCitation


class PersonaType(str, Enum):
    CEO = "CEO"
    CFO = "CFO"
    CTO = "CTO"
    CISO = "CISO"
    BI_ANALYST = "BI_ANALYST"


class EffortLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TimeHorizon(str, Enum):
    THIRTY_DAYS = "30 Days"
    NINETY_DAYS = "90 Days"
    ONE_YEAR = "1 Year"


class PersonaProfile(BaseModel):
    persona_type: PersonaType
    display_title: str
    focus_areas: List[str]
    tone: str
    description: str


class BusinessRecommendationCard(BaseModel):
    id: str
    title: str
    description: str
    expected_impact_usd: float
    effort_level: EffortLevel
    time_horizon: TimeHorizon
    department: str
    priority_rank: int


class AssistantChatResponse(BaseModel):
    session_id: str
    persona: str
    response: str
    intent: str
    confidence_score: float
    latency_ms: float
    citations: List[RAGCitation] = []
    recommendations: List[BusinessRecommendationCard] = []
