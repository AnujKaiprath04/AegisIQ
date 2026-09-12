from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.analytics_engine.types import (
    AnalyticsExecutionResult,
    AnalyticsJobType,
    AnalyticsTaskStatus,
    ExecutiveAnalyticsOverview,
)


class AnalyticsJobRequestSchema(BaseModel):
    job_type: AnalyticsJobType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset_id: Optional[str] = None


class AnalyticsExecutionResultSchema(BaseModel):
    job_id: str
    job_type: AnalyticsJobType
    status: AnalyticsTaskStatus
    created_at: str
    completed_at: Optional[str] = None
    execution_time_ms: float
    predictions: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    error_message: Optional[str] = None


class ExecutiveAnalyticsOverviewSchema(BaseModel):
    timestamp: str
    financial_forecast: Dict[str, Any] = {}
    churn_risk_summary: Dict[str, Any] = {}
    anomaly_posture: Dict[str, Any] = {}
    risk_scorecard: Dict[str, Any] = {}
    active_models_count: int
    average_model_confidence: float


class AnalyticsTelemetrySchema(BaseModel):
    engine_status: str
    active_ml_models: List[Dict[str, Any]] = []
    total_inferences_served: int
    average_inference_latency_ms: float
    p95_inference_latency_ms: float
    prediction_cache_hit_rate: float
    automated_retraining_schedule: str


class AnalyticsJobListResponse(BaseModel):
    total_jobs: int
    jobs: List[AnalyticsExecutionResultSchema] = []
