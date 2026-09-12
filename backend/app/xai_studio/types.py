from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class XAITechnique(str, Enum):
    SHAP_TREE = "SHAP_TREE"
    SHAP_KERNEL = "SHAP_KERNEL"
    LIME_SURROGATE = "LIME_SURROGATE"
    PERMUTATION_IMPORTANCE = "PERMUTATION_IMPORTANCE"
    COUNTERFACTUAL_OPTIMIZER = "COUNTERFACTUAL_OPTIMIZER"


class FeatureAttribution(BaseModel):
    feature_name: str
    actual_value: Any
    attribution_weight: float = Field(..., description="Positive increases prediction, negative decreases")
    impact_direction: str = Field(..., description="POSITIVE_RISK or NEGATIVE_RISK")
    relative_percentage: float = Field(..., ge=0.0, le=100.0)


class XAIExplanationResult(BaseModel):
    model_id: str
    prediction_label: str
    prediction_probability: float = Field(..., ge=0.0, le=1.0)
    base_value: float = Field(..., description="Baseline expectation value E[f(x)]")
    shap_values: List[FeatureAttribution] = []
    lime_values: List[FeatureAttribution] = []
    natural_language_explanation: str
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)


class CounterfactualScenario(BaseModel):
    original_probability: float
    target_probability: float
    feature_interventions: Dict[str, Any] = {}
    feasibility_score: float = Field(..., ge=0.0, le=1.0)
    estimated_effort: str
    actionable_summary: str


class GlobalFeatureRanking(BaseModel):
    feature_name: str
    importance_score: float = Field(..., ge=0.0, le=1.0)
    rank: int
    domain: str


class ModelTransparencyCard(BaseModel):
    model_id: str
    model_name: str
    version: str
    task_type: str
    training_records_count: int
    disparate_impact_ratio: float = Field(default=1.04, description="Optimal range 0.80 - 1.25")
    demographic_parity_diff: float = Field(default=0.02, description="Optimal < 0.10")
    compliance_status: str
    governance_notes: str
