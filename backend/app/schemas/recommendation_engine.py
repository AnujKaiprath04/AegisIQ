from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.recommendation_engine.types import (
    ImplementationEffort,
    RecommendationCard,
    RecommendationCategory,
    RecommendationCategorySummary,
    RecommendationPriority,
    RecommendationStatus,
    TimeHorizon,
)


class RecommendationCardSchema(RecommendationCard):
    pass


class RecommendationListResponse(BaseModel):
    total_recommendations: int
    total_potential_roi_usd: float
    recommendations: List[RecommendationCardSchema] = []


class RecommendationGenerateRequest(BaseModel):
    target_type: str = Field(..., description="Target entity type e.g. ACCOUNT, INVENTORY, CLOUD")
    target_id: str = Field(..., description="Target identifier e.g. ACC-APEX-001 or SKU-OPT-100")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RecommendationGenerateResponse(BaseModel):
    generated_count: int
    recommendations: List[RecommendationCardSchema] = []


class RecommendationApplyResponse(BaseModel):
    success: bool
    message: str
    recommendation: RecommendationCardSchema


class RecommendationCategorySummarySchema(RecommendationCategorySummary):
    pass


class RecommendationCategoriesResponse(BaseModel):
    total_categories: int
    total_potential_roi_all_categories_usd: float
    categories: List[RecommendationCategorySummarySchema] = []
