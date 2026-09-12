from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.integration import (
    ConnectionCreate,
    ConnectionSummary,
    ConnectionTestResult,
    IngestionJobCreate,
    IngestionJobResponse,
    JobRunTriggerResponse,
    SchemaTreeResponse,
)
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/integration", tags=["Module 2: Enterprise Data Integration"])


@router.get("/connections", response_model=List[ConnectionSummary])
def list_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst", "Executive", "Viewer"])),
):
    """List all registered enterprise data source connections with diagnostic health states."""
    connections = IntegrationService.get_connections(db=db)
    return [ConnectionSummary(**c) for c in connections]


@router.post("/connections", response_model=ConnectionSummary, status_code=status.HTTP_201_CREATED)
def create_connection(
    conn_in: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Register a new enterprise data source (PostgreSQL, MySQL, SQLite, MongoDB, REST API)."""
    conn = IntegrationService.create_connection(db=db, conn_in=conn_in, user=current_user)
    return ConnectionSummary(
        id=conn.id,
        name=conn.name,
        description=conn.description,
        connection_type=conn.connection_type,
        host=conn.host,
        port=conn.port,
        database_name=conn.database_name,
        api_endpoint_url=conn.api_endpoint_url,
        status=conn.status,
        latency_ms=conn.latency_ms,
        ssl_enabled=conn.ssl_enabled,
        last_tested_at=conn.last_tested_at,
        tables_count=0,
        created_at=conn.created_at,
    )


@router.post("/connections/{connection_id}/test", response_model=ConnectionTestResult)
def test_connection_health(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst"])),
):
    """Execute real-time connection ping, measure latency in milliseconds, and verify SSL certificate."""
    return IntegrationService.test_connection(db=db, connection_id=connection_id)


@router.get("/connections/{connection_id}/schema", response_model=SchemaTreeResponse)
def get_discovered_schema(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst", "Executive", "Viewer"])),
):
    """Fetch discovered tables, views, collections, and column metadata catalog for connection."""
    return IntegrationService.get_schema_tree(db=db, connection_id=connection_id)


@router.post("/connections/{connection_id}/discover", status_code=status.HTTP_200_OK)
def trigger_schema_discovery(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Trigger on-demand schema introspection to discover newly added tables and columns."""
    count = IntegrationService.discover_schema(db=db, connection_id=connection_id)
    return {"message": f"Schema discovery completed. {count} new tables/endpoints cataloged."}


@router.get("/jobs", response_model=List[IngestionJobResponse])
def list_ingestion_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst"])),
):
    """List scheduled and manual data ingestion synchronization jobs."""
    jobs = IntegrationService.get_ingestion_jobs(db=db)
    return [IngestionJobResponse.model_validate(j) for j in jobs]


@router.post("/jobs", response_model=IngestionJobResponse, status_code=status.HTTP_201_CREATED)
def create_ingestion_job(
    job_in: IngestionJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Configure a new data synchronization / ingestion job."""
    job = IntegrationService.create_ingestion_job(db=db, job_in=job_in)
    return IngestionJobResponse.model_validate(job)


@router.post("/jobs/{job_id}/run", response_model=JobRunTriggerResponse)
def run_ingestion_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Trigger manual execution of an enterprise data ingestion sync job."""
    job = IntegrationService.run_ingestion_job(db=db, job_id=job_id)
    return JobRunTriggerResponse(
        job_id=job.id,
        status=job.status,
        rows_ingested=job.rows_ingested,
        duration_seconds=job.duration_seconds,
        message=f"Sync job '{job.job_name}' completed in {job.duration_seconds}s. Ingested {job.rows_ingested} records.",
    )
