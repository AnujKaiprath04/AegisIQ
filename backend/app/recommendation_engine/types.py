from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationCategory(str, Enum):
    PRODUCT_PROMOTION = "PRODUCT_PROMOTION"
    INVENTORY_RESTOCKING = "INVENTORY_RESTOCKING"
    CUSTOMER_RETENTION = "CUSTOMER_RETENTION"
    MARKETING_CAMPAIGN = "MARKETING_CAMPAIGN"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    REVENUE_IMPROVEMENT = "REVENUE_IMPROVEMENT"
    OPERATIONAL_WORKFLOW = "OPERATIONAL_WORKFLOW"


class RecommendationPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ImplementationEffort(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TimeHorizon(str, Enum):
    IMMEDIATE_24H = "IMMEDIATE_24H"
    NEXT_30_DAYS = "NEXT_30_DAYS"
    QUARTERLY_PLAN = "QUARTERLY_PLAN"


class RecommendationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    APPLIED = "APPLIED"
    DISMISSED = "DISMISSED"


class RecommendationCard(BaseModel):
    recommendation_id: str
    category: RecommendationCategory
    title: str
    description: str
    priority: RecommendationPriority
    implementation_effort: ImplementationEffort
    time_horizon: TimeHorizon
    expected_roi_usd: float = Field(default=0.0, ge=0.0)
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0)
    rationale: str
    action_steps: List[str] = []
    target_entity: Optional[str] = None
    status: RecommendationStatus = RecommendationStatus.ACTIVE
    created_at: str
    applied_at: Optional[str] = None


class RecommendationCategorySummary(BaseModel):
    category: RecommendationCategory
    active_count: int
    applied_count: int
    total_potential_roi_usd: float
