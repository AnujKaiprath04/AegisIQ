from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.recommendation_engine import (
    RecommendationApplyResponse,
    RecommendationCardSchema,
    RecommendationCategoriesResponse,
    RecommendationCategorySummarySchema,
    RecommendationGenerateRequest,
    RecommendationGenerateResponse,
    RecommendationListResponse,
)
from app.recommendation_engine.engine import EnterpriseRecommendationEngine
from app.recommendation_engine.types import (
    RecommendationCategory,
    RecommendationPriority,
    RecommendationStatus,
)

router = APIRouter(prefix="/ml/recommendations", tags=["Part 3 - Module 4: Recommendation Engine"])


@router.get("", response_model=RecommendationListResponse)
def list_recommendations(
    category: Optional[RecommendationCategory] = Query(None, description="Filter by category"),
    priority: Optional[RecommendationPriority] = Query(None, description="Filter by priority level"),
    status: Optional[RecommendationStatus] = Query(None, description="Filter by active/applied status"),
    current_user: User = Depends(get_current_user),
):
    """List active enterprise recommendations sorted by highest expected ROI ($USD)."""
    cards = EnterpriseRecommendationEngine.list_recommendations(
        category=category,
        priority=priority,
        status_filter=status,
    )
    total_roi = sum(c.expected_roi_usd for c in cards)
    return RecommendationListResponse(
        total_recommendations=len(cards),
        total_potential_roi_usd=round(total_roi, 2),
        recommendations=[RecommendationCardSchema(**c.model_dump()) for c in cards],
    )


@router.post("/generate", response_model=RecommendationGenerateResponse)
def generate_recommendations(
    req: RecommendationGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate prescriptive recommendations on demand for a customer account, inventory SKU, or cost center."""
    cards = EnterpriseRecommendationEngine.generate_recommendations(
        target_type=req.target_type,
        target_id=req.target_id,
        parameters=req.parameters,
    )
    return RecommendationGenerateResponse(
        generated_count=len(cards),
        recommendations=[RecommendationCardSchema(**c.model_dump()) for c in cards],
    )


@router.post("/{recommendation_id}/apply", response_model=RecommendationApplyResponse)
def apply_recommendation(
    recommendation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Adopt and mark a recommendation card as applied in the platform audit trail."""
    card = EnterpriseRecommendationEngine.apply_recommendation(recommendation_id)
    return RecommendationApplyResponse(
        success=True,
        message=f"Recommendation '{card.title}' successfully marked as APPLIED by {current_user.email}.",
        recommendation=RecommendationCardSchema(**card.model_dump()),
    )


@router.get("/categories", response_model=RecommendationCategoriesResponse)
def get_recommendation_categories_summary(
    current_user: User = Depends(get_current_user),
):
    """Retrieve category-level breakdown of recommendation counts and total potential ROI."""
    summaries = EnterpriseRecommendationEngine.get_category_summary()
    total_roi = sum(s.total_potential_roi_usd for s in summaries)
    return RecommendationCategoriesResponse(
        total_categories=len(summaries),
        total_potential_roi_all_categories_usd=round(total_roi, 2),
        categories=[RecommendationCategorySummarySchema(**s.model_dump()) for s in summaries],
    )
