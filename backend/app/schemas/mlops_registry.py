from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.mlops_registry.types import (
    DriftMetric,
    FrameworkType,
    MasterIntelligenceStatus,
    ModelStage,
    ModelVersion,
    RegisteredModel,
    RetrainingJob,
)


class ModelVersionSchema(ModelVersion):
    pass


class RegisteredModelSchema(RegisteredModel):
    pass


class DriftMetricSchema(DriftMetric):
    pass


class RetrainingJobSchema(RetrainingJob):
    pass


class MasterIntelligenceStatusSchema(MasterIntelligenceStatus):
    pass


class ModelListResponse(BaseModel):
    total_models: int
    models: List[RegisteredModelSchema] = []


class ModelDriftResponse(BaseModel):
    model_id: str
    total_features: int
    metrics: List[DriftMetricSchema] = []


class CanaryDeployRequest(BaseModel):
    canary_split_pct: float = Field(..., ge=0.0, le=100.0, description="Percentage of traffic routed to canary version (0-100)")


class ModelPromoteRequest(BaseModel):
    version_str: str = Field(..., description="Version string to promote to active PRODUCTION stage e.g. v2.5.0-rc1")


class FullIntelligenceSweepResponse(BaseModel):
    sweep_id: str
    execution_status: str
    execution_latency_ms: float
    timestamp: str
    modules_evaluated: List[str] = []
    executive_summary: Dict[str, Any] = {}
    predictive_signals: Dict[str, Any] = {}
    prescriptive_recommendations_count: int
    composite_business_risk_score: float
    zero_trust_security_score: float
    stream_anomaly_detected: bool
    xai_primary_risk_driver: str
    configured_alert_rules_count: int
