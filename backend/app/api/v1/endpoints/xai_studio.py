from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.xai_studio import (
    CounterfactualRequest,
    CounterfactualResponse,
    CounterfactualScenarioSchema,
    GlobalFeatureImportanceResponse,
    GlobalFeatureRankingSchema,
    ModelTransparencyCardSchema,
    ModelTransparencyResponse,
    XAIExplainRequest,
    XAIExplainResponse,
    XAIExplanationResultSchema,
)
from app.xai_studio.engine import EnterpriseXAIStudioEngine

router = APIRouter(prefix="/ml/xai", tags=["Explainable AI (XAI) Studio"])


@router.post("/explain", response_model=XAIExplainResponse)
def explain_prediction(
    req: XAIExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate SHAP and LIME additive feature attributions with natural language executive explanations."""
    result = EnterpriseXAIStudioEngine.explain_prediction(
        model_id=req.model_id,
        input_features=req.input_features,
        probability=req.prediction_probability,
    )
    return XAIExplainResponse(explanation=XAIExplanationResultSchema(**result.model_dump()))


@router.post("/counterfactual", response_model=CounterfactualResponse)
def simulate_counterfactual(
    req: CounterfactualRequest,
    current_user: User = Depends(get_current_user),
):
    """Simulate counterfactual 'What-If' conditions required to flip a high-risk model prediction."""
    scenario = EnterpriseXAIStudioEngine.simulate_counterfactual(
        model_id=req.model_id,
        input_features=req.input_features,
        current_probability=req.current_probability,
        target_probability=req.target_probability,
    )
    return CounterfactualResponse(scenario=CounterfactualScenarioSchema(**scenario.model_dump()))


@router.get("/feature-importance/{model_id}", response_model=GlobalFeatureImportanceResponse)
def get_global_feature_importance(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve global dataset-level feature importance rankings and Gini impurity metrics."""
    rankings = EnterpriseXAIStudioEngine.get_global_feature_importance(model_id)
    return GlobalFeatureImportanceResponse(
        model_id=model_id,
        total_features=len(rankings),
        rankings=[GlobalFeatureRankingSchema(**r.model_dump()) for r in rankings],
    )


@router.get("/model-transparency/{model_id}", response_model=ModelTransparencyResponse)
def get_model_transparency(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve model lineage, fairness and bias audit metrics (EU AI Act & DORA compliance)."""
    card = EnterpriseXAIStudioEngine.get_model_transparency(model_id)
    return ModelTransparencyResponse(card=ModelTransparencyCardSchema(**card.model_dump()))
