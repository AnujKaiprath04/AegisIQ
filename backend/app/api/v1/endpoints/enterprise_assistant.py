from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.enterprise_assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    KPIExplainRequest,
    KPIExplainResponse,
    PersonaListResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.assistant_service.assistant import EnterpriseAIAssistant
from app.assistant_service.personas import PersonaEngine
from app.assistant_service.recommendations import BusinessRecommendationEngine
from app.assistant_service.types import PersonaType

router = APIRouter(prefix="/ai/assistant", tags=["Part 2 - Module 7: Enterprise AI Assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(
    req: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute conversational decision query with multi-persona reasoning and action recommendations."""
    return EnterpriseAIAssistant.chat(
        query=req.query,
        persona=req.persona or PersonaType.CEO,
        session_id=req.session_id,
    )


@router.post("/recommendations", response_model=RecommendationResponse)
def generate_recommendations(
    req: RecommendationRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate prioritized business recommendation action cards with financial ROI and effort levels."""
    cards = BusinessRecommendationEngine.generate_recommendations(
        topic_or_query=req.topic,
        persona_type=req.persona or PersonaType.CEO,
    )
    return RecommendationResponse(
        topic=req.topic,
        persona=(req.persona or PersonaType.CEO).value,
        recommendations=cards,
    )


@router.post("/kpi-explain", response_model=KPIExplainResponse)
def explain_kpi_root_cause(
    req: KPIExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute deep-dive root-cause analysis and driver attribution for business KPIs."""
    res = EnterpriseAIAssistant.explain_kpi(
        kpi_name=req.kpi_name,
        persona=req.persona or PersonaType.CFO,
    )
    return KPIExplainResponse(**res)


@router.get("/personas", response_model=PersonaListResponse)
def list_personas(
    current_user: User = Depends(get_current_user),
):
    """List available executive reasoning personas (CEO, CFO, CTO, CISO, BI Analyst)."""
    return PersonaListResponse(
        active_default="CEO",
        personas=PersonaEngine.list_personas(),
    )
