from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyticsJobType(str, Enum):
    REVENUE_FORECAST = "REVENUE_FORECAST"
    CUSTOMER_CHURN_ANALYSIS = "CUSTOMER_CHURN_ANALYSIS"
    ANOMALY_DETECTION_SCAN = "ANOMALY_DETECTION_SCAN"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    CROSS_DOMAIN_SWEEP = "CROSS_DOMAIN_SWEEP"


class AnalyticsTaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalyticsJobRequest(BaseModel):
    job_type: AnalyticsJobType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dataset_id: Optional[str] = None


class AnalyticsExecutionResult(BaseModel):
    job_id: str
    job_type: AnalyticsJobType
    status: AnalyticsTaskStatus
    created_at: str
    completed_at: Optional[str] = None
    execution_time_ms: float = 0.0
    predictions: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    error_message: Optional[str] = None


class ExecutiveAnalyticsOverview(BaseModel):
    timestamp: str
    financial_forecast: Dict[str, Any] = {}
    churn_risk_summary: Dict[str, Any] = {}
    anomaly_posture: Dict[str, Any] = {}
    risk_scorecard: Dict[str, Any] = {}
    active_models_count: int
    average_model_confidence: float
