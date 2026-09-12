from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnomalyMethod(str, Enum):
    Z_SCORE = "Z_SCORE"
    IQR = "IQR"
    ISOLATION_FOREST = "ISOLATION_FOREST"
    MAHALANOBIS = "MAHALANOBIS"
    ENSEMBLE = "ENSEMBLE"


class AnomalySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NORMAL = "NORMAL"


class AnomalyDomain(str, Enum):
    FINANCIAL = "FINANCIAL"
    SYSTEM_TELEMETRY = "SYSTEM_TELEMETRY"
    USER_BEHAVIOR = "USER_BEHAVIOR"
    REVENUE = "REVENUE"


class AnomalyPoint(BaseModel):
    timestamp: str
    value: float
    is_anomaly: bool
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    severity: AnomalySeverity
    method_used: AnomalyMethod
    expected_range: List[float] = []
    explanation: str


class BatchAnomalyResult(BaseModel):
    total_records: int
    anomaly_count: int
    anomaly_percentage: float
    method_used: AnomalyMethod
    anomalies: List[AnomalyPoint] = []
    execution_time_ms: float


class DomainProfile(BaseModel):
    domain: AnomalyDomain
    metric_name: str
    baseline_mean: float
    baseline_std: float
    iqr_lower: float
    iqr_upper: float
    threshold: float
