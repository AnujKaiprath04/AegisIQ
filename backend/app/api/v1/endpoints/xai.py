from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.xai import (
    GlobalFeatureImportanceResponse,
    ModelFairnessMetricsResponse,
    WaterfallExplanationResponse,
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
)
from app.services.xai_service import XAIService

router = APIRouter(prefix="/xai", tags=["Explainable AI & Feature Importance"])


@router.get("/global-importance", response_model=GlobalFeatureImportanceResponse)
def get_global_feature_importance(
    model_type: str = Query("CHURN_CLASSIFICATION", description="CHURN_CLASSIFICATION, REVENUE_FORECAST"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve global SHAP / LIME feature importance rankings and relative predictive weightings."""
    return XAIService.get_global_feature_importance(db=db, model_type=model_type)


@router.get("/explain", response_model=WaterfallExplanationResponse)
def get_waterfall_explanation(
    entity_id: Optional[int] = Query(None, description="Optional customer account ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deconstruct an individual machine learning decision step-by-step from Base Value to final Probability."""
    return XAIService.get_waterfall_explanation(db=db, entity_id=entity_id)


@router.post("/what-if", response_model=WhatIfSimulationResponse)
def run_what_if_simulation(
    req: WhatIfSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute real-time counterfactual simulation adjusting account parameters to calculate updated risk."""
    return XAIService.run_what_if_simulation(db=db, req=req, user=current_user)


@router.get("/fairness", response_model=ModelFairnessMetricsResponse)
def get_model_fairness_metrics(
    current_user: User = Depends(get_current_user),
):
    """Retrieve algorithmic fairness, demographic parity, and bias evaluation scorecard."""
    return XAIService.get_fairness_metrics()
