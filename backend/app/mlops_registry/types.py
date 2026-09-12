from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelStage(str, Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    CANARY = "CANARY"
    ARCHIVED = "ARCHIVED"


class FrameworkType(str, Enum):
    XGBOOST = "XGBOOST"
    SCIKIT_LEARN = "SCIKIT_LEARN"
    ARIMA_STATS = "ARIMA_STATS"
    PYTORCH = "PYTORCH"
    OPERATIONS_RESEARCH = "OPERATIONS_RESEARCH"


class DriftStatus(str, Enum):
    NO_DRIFT = "NO_DRIFT"
    MODERATE_DRIFT = "MODERATE_DRIFT"
    CRITICAL_DRIFT = "CRITICAL_DRIFT"


class ModelVersion(BaseModel):
    version_id: str
    version_str: str
    stage: ModelStage
    accuracy_metric_name: str
    accuracy_score: float
    created_at: str
    deployed_at: Optional[str] = None


class RegisteredModel(BaseModel):
    model_id: str
    model_name: str
    description: str
    framework: FrameworkType
    active_version: str
    all_versions: List[ModelVersion] = []
    canary_traffic_split_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    last_retrained_at: str


class DriftMetric(BaseModel):
    feature_name: str
    psi_score: float = Field(..., ge=0.0, description="Population Stability Index (<0.10 No Drift, 0.1-0.25 Moderate, >0.25 Critical)")
    ks_statistic: float = Field(..., ge=0.0, le=1.0, description="Kolmogorov-Smirnov test statistic")
    p_value: float = Field(..., ge=0.0, le=1.0)
    drift_status: DriftStatus
    baseline_mean: float
    current_mean: float


class RetrainingJob(BaseModel):
    job_id: str
    model_id: str
    status: str
    triggered_by: str
    baseline_metric: float
    new_metric: float
    improvement_pct: float
    created_at: str
    completed_at: str


class MasterIntelligenceStatus(BaseModel):
    total_modules_active: int = 10
    system_health: str
    active_models_count: int
    active_recommendations_count: int
    composite_risk_score: float
    zero_trust_security_score: float
    active_anomalies_count: int
    active_alert_rules_count: int
    last_full_sweep_at: str
