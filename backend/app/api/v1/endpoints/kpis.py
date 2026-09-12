from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.kpi import (
    KPICalculateRequest,
    KPICalculateResponse,
    KPIMetricResponse,
    KPITargetUpdate,
)
from app.services.kpi_service import KPIService

router = APIRouter(prefix="/kpis", tags=["Enterprise KPI Engine"])


@router.get("", response_model=List[KPIMetricResponse])
def list_kpi_metrics(
    category: Optional[str] = Query(None, description="FINANCIAL, SALES, OPERATIONS, CUSTOMERS"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Retrieve catalog of computed enterprise KPIs with actual vs target values."""
    metrics = KPIService.get_all_kpis(db=db, category=category)
    return [KPIMetricResponse.model_validate(m) for m in metrics]


@router.put("/{kpi_id}/target", response_model=KPIMetricResponse)
def update_kpi_target(
    kpi_id: int,
    target_in: KPITargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst"])),
):
    """Update KPI target threshold and recompute variance percentages."""
    return KPIService.update_kpi_target(db=db, kpi_id=kpi_id, target_in=target_in)


@router.post("/calculate", response_model=KPICalculateResponse, status_code=status.HTTP_200_OK)
def calculate_custom_kpi(
    calc_req: KPICalculateRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst"])),
):
    """Dynamically evaluate custom formula expressions (Gross Margin, CAC, LTV/CAC, Quick Ratio, etc.)."""
    return KPIService.calculate_custom_formula(calc_req)
