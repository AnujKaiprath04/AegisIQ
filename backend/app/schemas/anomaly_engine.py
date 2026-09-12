from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.anomaly_engine.types import (
    AnomalyDomain,
    AnomalyMethod,
    AnomalyPoint,
    AnomalySeverity,
    BatchAnomalyResult,
    DomainProfile,
)


class AnomalyPointSchema(AnomalyPoint):
    pass


class BatchAnomalyResultSchema(BatchAnomalyResult):
    pass


class DomainProfileSchema(DomainProfile):
    pass


class StreamAnomalyRequest(BaseModel):
    domain: AnomalyDomain = Field(..., description="Business or system domain (FINANCIAL, SYSTEM_TELEMETRY, etc.)")
    value: float = Field(..., description="Observed numeric metric value")
    method: AnomalyMethod = Field(default=AnomalyMethod.ENSEMBLE)


class StreamAnomalyResponse(BaseModel):
    point: AnomalyPointSchema


class BatchAnomalyRequest(BaseModel):
    values: List[float] = Field(..., description="List of numerical values to scan for outliers")
    method: AnomalyMethod = Field(default=AnomalyMethod.Z_SCORE)
    threshold: float = Field(default=3.0, ge=1.0, le=10.0)


class BatchAnomalyResponse(BaseModel):
    result: BatchAnomalyResultSchema


class AnomalyProfilesResponse(BaseModel):
    total_profiles: int
    profiles: List[DomainProfileSchema] = []


class RecentAnomaliesResponse(BaseModel):
    total_recent_anomalies: int
    anomalies: List[AnomalyPointSchema] = []
