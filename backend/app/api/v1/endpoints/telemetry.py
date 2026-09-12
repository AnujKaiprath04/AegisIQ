from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.telemetry import (
    DatabasePoolMetrics,
    FullTelemetrySnapshotResponse,
    SubsystemHealth,
)
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Telemetry, APM & Health Monitoring"])


@router.get("/dashboard", response_model=FullTelemetrySnapshotResponse)
def get_telemetry_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve complete APM telemetry snapshot, host resources, and latency percentiles."""
    return TelemetryService.get_dashboard_snapshot(db=db)


@router.get("/subsystems", response_model=List[SubsystemHealth])
def get_subsystems_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Probe real-time health across all 6 core platform microservices."""
    return TelemetryService.get_subsystems_health(db=db)


@router.get("/db-pool", response_model=DatabasePoolMetrics)
def get_database_pool_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve PostgreSQL connection pool utilization and query latency metrics."""
    return TelemetryService.get_database_pool_metrics()


@router.get("/prometheus", response_class=Response)
def get_prometheus_metrics(
    db: Session = Depends(get_db),
):
    """Expose live telemetry in standard Prometheus exposition format."""
    content = TelemetryService.get_prometheus_exposition(db=db)
    return Response(content=content, media_type="text/plain; version=0.0.4")
