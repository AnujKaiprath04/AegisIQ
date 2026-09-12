from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RiskPillar(str, Enum):
    REVENUE_DECLINE = "REVENUE_DECLINE"
    CUSTOMER_LOSS = "CUSTOMER_LOSS"
    LOW_PERFORMING_PRODUCT = "LOW_PERFORMING_PRODUCT"
    OPERATIONAL_BOTTLENECK = "OPERATIONAL_BOTTLENECK"
    FINANCIAL_ANOMALY = "FINANCIAL_ANOMALY"
    SUPPLY_CHAIN_DISRUPTION = "SUPPLY_CHAIN_DISRUPTION"


class RiskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    MINIMAL = "MINIMAL"


class RiskTrend(str, Enum):
    INCREASING = "INCREASING"
    STABLE = "STABLE"
    DECREASING = "DECREASING"


class BusinessRiskItem(BaseModel):
    risk_id: str
    pillar: RiskPillar
    title: str
    description: str
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk index between 0 and 100")
    priority_level: RiskPriority
    financial_exposure_usd: float = Field(default=0.0, ge=0.0)
    likelihood_score: int = Field(default=2, ge=1, le=5, description="Likelihood on scale 1-5")
    impact_score: int = Field(default=2, ge=1, le=5, description="Impact on scale 1-5")
    mitigation_actions: List[str] = []
    trend: RiskTrend = RiskTrend.STABLE
    last_assessed_at: str


class EnterpriseRiskScorecard(BaseModel):
    composite_risk_score: float
    risk_status: str
    total_financial_exposure_usd: float
    pillar_breakdown: Dict[str, float] = {}
    active_risks_count: int
    highest_priority_risk: str
    assessment_timestamp: str


class RiskHeatmapPoint(BaseModel):
    risk_id: str
    title: str
    pillar: RiskPillar
    likelihood: int
    impact: int
    risk_score: float
    priority: RiskPriority
