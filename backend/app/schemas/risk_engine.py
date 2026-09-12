from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.risk_engine.types import (
    BusinessRiskItem,
    EnterpriseRiskScorecard,
    RiskHeatmapPoint,
    RiskPillar,
    RiskPriority,
    RiskTrend,
)


class BusinessRiskItemSchema(BusinessRiskItem):
    pass


class EnterpriseRiskScorecardSchema(EnterpriseRiskScorecard):
    pass


class RiskHeatmapPointSchema(RiskHeatmapPoint):
    pass


class RiskEvaluationRequest(BaseModel):
    pillar: RiskPillar
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RiskHeatmapResponse(BaseModel):
    total_points: int
    matrix_dimension: str = "5x5 (Likelihood vs Impact)"
    points: List[RiskHeatmapPointSchema] = []


class RiskItemListResponse(BaseModel):
    total_risks: int
    total_financial_exposure_usd: float
    risks: List[BusinessRiskItemSchema] = []
