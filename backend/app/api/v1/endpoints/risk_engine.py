from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.risk_engine import (
    BusinessRiskItemSchema,
    EnterpriseRiskScorecardSchema,
    RiskEvaluationRequest,
    RiskHeatmapPointSchema,
    RiskHeatmapResponse,
    RiskItemListResponse,
)
from app.risk_engine.engine import BusinessRiskIntelligenceEngine
from app.risk_engine.types import RiskPillar, RiskPriority

router = APIRouter(prefix="/ml/risks", tags=["Part 3 - Module 5: Business Risk Intelligence"])


@router.get("/scorecard", response_model=EnterpriseRiskScorecardSchema)
def get_enterprise_risk_scorecard(
    current_user: User = Depends(get_current_user),
):
    """Retrieve global enterprise risk scorecard with composite score, status, and financial exposure."""
    scorecard = BusinessRiskIntelligenceEngine.get_scorecard()
    return EnterpriseRiskScorecardSchema(**scorecard.model_dump())


@router.get("/items", response_model=RiskItemListResponse)
def list_risk_items(
    pillar: Optional[RiskPillar] = Query(None, description="Filter by risk pillar"),
    priority: Optional[RiskPriority] = Query(None, description="Filter by priority level"),
    current_user: User = Depends(get_current_user),
):
    """List all identified enterprise risk items sorted by risk score descending."""
    items = BusinessRiskIntelligenceEngine.list_risk_items(pillar=pillar, priority=priority)
    total_exposure = sum(i.financial_exposure_usd for i in items)
    return RiskItemListResponse(
        total_risks=len(items),
        total_financial_exposure_usd=round(total_exposure, 2),
        risks=[BusinessRiskItemSchema(**i.model_dump()) for i in items],
    )


@router.post("/evaluate", response_model=BusinessRiskItemSchema)
def evaluate_risk_domain(
    req: RiskEvaluationRequest,
    current_user: User = Depends(get_current_user),
):
    """Trigger real-time risk assessment for a specific business pillar (Revenue, Churn, Supply Chain)."""
    item = BusinessRiskIntelligenceEngine.evaluate_domain(pillar=req.pillar, parameters=req.parameters)
    return BusinessRiskItemSchema(**item.model_dump())


@router.get("/heatmap", response_model=RiskHeatmapResponse)
def get_risk_heatmap(
    current_user: User = Depends(get_current_user),
):
    """Retrieve matrix coordinate data for executive risk heatmap visualization (Likelihood vs Impact)."""
    points = BusinessRiskIntelligenceEngine.get_heatmap_data()
    return RiskHeatmapResponse(
        total_points=len(points),
        matrix_dimension="5x5 (Likelihood vs Impact)",
        points=[RiskHeatmapPointSchema(**p.model_dump()) for p in points],
    )
