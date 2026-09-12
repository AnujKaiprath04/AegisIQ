from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.xai_studio.types import (
    CounterfactualScenario,
    FeatureAttribution,
    GlobalFeatureRanking,
    ModelTransparencyCard,
    XAIExplanationResult,
)


class FeatureAttributionSchema(FeatureAttribution):
    pass


class XAIExplanationResultSchema(XAIExplanationResult):
    pass


class CounterfactualScenarioSchema(CounterfactualScenario):
    pass


class GlobalFeatureRankingSchema(GlobalFeatureRanking):
    pass


class ModelTransparencyCardSchema(ModelTransparencyCard):
    pass


class XAIExplainRequest(BaseModel):
    model_id: str = Field(default="customer_churn_xgboost", description="Target ML model identifier")
    input_features: Dict[str, Any] = Field(default_factory=dict)
    prediction_probability: float = Field(default=0.74, ge=0.0, le=1.0)


class XAIExplainResponse(BaseModel):
    explanation: XAIExplanationResultSchema


class CounterfactualRequest(BaseModel):
    model_id: str = Field(default="customer_churn_xgboost")
    input_features: Dict[str, Any] = Field(default_factory=dict)
    current_probability: float = Field(default=0.74, ge=0.0, le=1.0)
    target_probability: float = Field(default=0.18, ge=0.0, le=1.0)


class CounterfactualResponse(BaseModel):
    scenario: CounterfactualScenarioSchema


class GlobalFeatureImportanceResponse(BaseModel):
    model_id: str
    total_features: int
    rankings: List[GlobalFeatureRankingSchema] = []


class ModelTransparencyResponse(BaseModel):
    card: ModelTransparencyCardSchema
