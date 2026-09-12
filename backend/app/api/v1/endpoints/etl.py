from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.etl import (
    DataQualityReportResponse,
    ETLConfig,
    ETLRunResponse,
)
from app.services.etl_service import ETLService

router = APIRouter(prefix="/etl", tags=["ETL Pipeline & Data Quality"])


@router.post("/clean", response_model=ETLRunResponse, status_code=status.HTTP_200_OK)
def execute_etl_pipeline(
    config: ETLConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Execute enterprise data cleaning transformation job and compute quality scorecard."""
    return ETLService.run_pipeline(db=db, config=config, user=current_user)


@router.get("/quality-report/{dataset_id}", response_model=DataQualityReportResponse)
def get_dataset_quality_scorecard(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst", "Executive", "Viewer"])),
):
    """Retrieve 4-pillar data quality report (Completeness, Uniqueness, Validity, Consistency)."""
    return ETLService.get_quality_report(db=db, dataset_id=dataset_id)


@router.get("/runs", response_model=List[ETLRunResponse])
def get_etl_run_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst"])),
):
    """List historical ETL pipeline executions and durations."""
    runs = ETLService.get_recent_runs(db=db, limit=limit)
    return [ETLRunResponse.model_validate(r) for r in runs]
