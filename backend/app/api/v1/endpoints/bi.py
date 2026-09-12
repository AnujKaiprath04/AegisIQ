from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.bi import (
    CustomerAnalyticsResponse,
    ExecutiveOverviewResponse,
    FinancialAnalyticsResponse,
    InventoryAnalyticsResponse,
    SalesAnalyticsResponse,
)
from app.services.bi_service import BIService

router = APIRouter(prefix="/bi", tags=["Business Intelligence & Analytics"])


@router.get("/overview", response_model=ExecutiveOverviewResponse)
def get_executive_overview(
    date_range: str = Query("YTD", description="MTD, QTD, YTD, 1Y, ALL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Consolidated executive-level business intelligence metrics and trends."""
    return BIService.get_executive_overview(db=db, date_range=date_range)


@router.get("/finance", response_model=FinancialAnalyticsResponse)
def get_financial_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst"])),
):
    """Financial domain metrics, margin histories, and expense allocations."""
    return BIService.get_financial_analytics(db=db)


@router.get("/sales", response_model=SalesAnalyticsResponse)
def get_sales_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Sales pipeline velocity, conversion funnel, and product line growth."""
    return BIService.get_sales_analytics(db=db)


@router.get("/customers", response_model=CustomerAnalyticsResponse)
def get_customer_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Customer cohort retention, net revenue retention, and churn risk distributions."""
    return BIService.get_customer_analytics(db=db)


@router.get("/inventory", response_model=InventoryAnalyticsResponse)
def get_inventory_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Supply chain inventory turnover, stock health, and supplier lead times."""
    return BIService.get_inventory_analytics(db=db)
