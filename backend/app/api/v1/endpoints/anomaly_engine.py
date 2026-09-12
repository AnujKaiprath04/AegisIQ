from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.anomaly_engine import (
    AnomalyPointSchema,
    AnomalyProfilesResponse,
    BatchAnomalyRequest,
    BatchAnomalyResponse,
    BatchAnomalyResultSchema,
    DomainProfileSchema,
    RecentAnomaliesResponse,
    StreamAnomalyRequest,
    StreamAnomalyResponse,
)
from app.anomaly_engine.engine import EnterpriseAnomalyEngine

router = APIRouter(prefix="/ml/anomalies", tags=["Part 3 - Module 7: Anomaly Detection Engine"])


@router.post("/detect-stream", response_model=StreamAnomalyResponse)
def detect_stream_anomaly(
    req: StreamAnomalyRequest,
    current_user: User = Depends(get_current_user),
):
    """Evaluate a single observed metric value against baseline distributions in real-time (<5ms)."""
    point = EnterpriseAnomalyEngine.detect_stream(
        domain=req.domain,
        value=req.value,
        method=req.method,
    )
    return StreamAnomalyResponse(point=AnomalyPointSchema(**point.model_dump()))


@router.post("/detect-batch", response_model=BatchAnomalyResponse)
def detect_batch_anomalies(
    req: BatchAnomalyRequest,
    current_user: User = Depends(get_current_user),
):
    """High-throughput batch dataset anomaly scanning with multi-method outlier scoring."""
    result = EnterpriseAnomalyEngine.detect_batch(
        values=req.values,
        method=req.method,
        threshold=req.threshold,
    )
    return BatchAnomalyResponse(result=BatchAnomalyResultSchema(**result.model_dump()))


@router.get("/profiles", response_model=AnomalyProfilesResponse)
def get_anomaly_profiles(
    current_user: User = Depends(get_current_user),
):
    """Retrieve pre-configured domain baseline distributions (Financial, Telemetry, User Behavior, Revenue)."""
    profiles = EnterpriseAnomalyEngine.get_profiles()
    return AnomalyProfilesResponse(
        total_profiles=len(profiles),
        profiles=[DomainProfileSchema(**p.model_dump()) for p in profiles],
    )


@router.get("/recent", response_model=RecentAnomaliesResponse)
def get_recent_anomalies(
    current_user: User = Depends(get_current_user),
):
    """Retrieve recently detected platform anomalies across all domains."""
    anomalies = EnterpriseAnomalyEngine.get_recent_anomalies()
    return RecentAnomaliesResponse(
        total_recent_anomalies=len(anomalies),
        anomalies=[AnomalyPointSchema(**a.model_dump()) for a in anomalies],
    )
