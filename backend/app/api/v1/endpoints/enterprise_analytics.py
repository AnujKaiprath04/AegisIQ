from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.enterprise_analytics import (
    AnalyticsExecutionResultSchema,
    AnalyticsJobListResponse,
    AnalyticsJobRequestSchema,
    AnalyticsTelemetrySchema,
    ExecutiveAnalyticsOverviewSchema,
)
from app.analytics_engine.dispatcher import AnalyticsJobDispatcher
from app.analytics_engine.engine import EnterpriseAnalyticsEngine

router = APIRouter(prefix="/ml/analytics", tags=["Part 3 - Module 1: Enterprise Analytics Engine"])


@router.get("/overview", response_model=ExecutiveAnalyticsOverviewSchema)
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
):
    """Retrieve unified executive cross-domain analytics overview across all ML dimensions."""
    overview = EnterpriseAnalyticsEngine.get_executive_overview()
    return ExecutiveAnalyticsOverviewSchema(**overview.model_dump())


@router.post("/dispatch", response_model=AnalyticsExecutionResultSchema, status_code=status.HTTP_201_CREATED)
def dispatch_analytics_job(
    req: AnalyticsJobRequestSchema,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Dispatch an ML analytics job (Revenue Forecast, Churn Analysis, Anomaly Scan, Risk Assessment)."""
    result = AnalyticsJobDispatcher.dispatch_job(
        job_type=req.job_type,
        parameters=req.parameters,
        dataset_id=req.dataset_id,
    )
    return AnalyticsExecutionResultSchema(**result.model_dump())


@router.get("/jobs/{job_id}", response_model=AnalyticsExecutionResultSchema)
def get_analytics_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve execution status, metrics, and prediction results for an analytics job."""
    result = AnalyticsJobDispatcher.get_job(job_id)
    return AnalyticsExecutionResultSchema(**result.model_dump())


@router.get("/jobs", response_model=AnalyticsJobListResponse)
def list_analytics_jobs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """List historical analytics execution jobs."""
    jobs = AnalyticsJobDispatcher.list_jobs(limit=limit)
    return AnalyticsJobListResponse(
        total_jobs=len(jobs),
        jobs=[AnalyticsExecutionResultSchema(**j.model_dump()) for j in jobs],
    )


@router.get("/telemetry", response_model=AnalyticsTelemetrySchema)
def get_analytics_telemetry(
    current_user: User = Depends(get_current_user),
):
    """Retrieve analytics engine throughput, latency percentiles, and active model health."""
    telemetry = EnterpriseAnalyticsEngine.get_telemetry()
    return AnalyticsTelemetrySchema(**telemetry)
