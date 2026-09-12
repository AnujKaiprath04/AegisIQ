from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.dataset import (
    DatasetDetail,
    DatasetPreview,
    DatasetSummary,
    DatasetUploadResponse,
)
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Enterprise Datasets & Ingestion"])


@router.get("", response_model=List[DatasetSummary])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Retrieve catalog of all registered enterprise datasets."""
    datasets = DatasetService.get_datasets(db=db)
    return [DatasetSummary.model_validate(d) for d in datasets]


@router.post("/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst"])),
):
    """Ingest structured dataset file (CSV, Excel, JSON) with schema introspection."""
    ds = DatasetService.upload_dataset(
        db=db,
        file=file,
        name=name,
        description=description,
        user=current_user,
    )
    return DatasetUploadResponse(
        message=f"Dataset '{ds.name}' successfully parsed and registered.",
        dataset=DatasetSummary.model_validate(ds),
    )


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset_details(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Get dataset schema, inferred column types, statistics, and quality score."""
    return DatasetService.get_dataset_detail(db=db, dataset_id=dataset_id)


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
def get_dataset_preview(
    dataset_id: int,
    limit: int = Query(50, ge=5, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Retrieve tabular data sample slice for interactive preview."""
    return DatasetService.get_dataset_preview(db=db, dataset_id=dataset_id, limit=limit)


@router.delete("/{dataset_id}", status_code=status.HTTP_200_OK)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Remove dataset and delete underlying stored file."""
    DatasetService.delete_dataset(db=db, dataset_id=dataset_id)
    return {"message": f"Dataset with ID {dataset_id} successfully deleted."}
