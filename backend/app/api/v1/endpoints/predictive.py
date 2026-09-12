from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.predictive import (
    CustomerChurnResponse,
    MLModelRegistrySummary,
    RetrainModelResponse,
    TimeSeriesForecastResponse,
)
from app.services.predictive_service import PredictiveService

router = APIRouter(prefix="/predictive", tags=["Module 11: Predictive Analytics & ML Forecasting"])


@router.get("/forecast/revenue", response_model=TimeSeriesForecastResponse)
def get_revenue_forecast(
    horizon_months: int = Query(12, ge=3, le=24, description="Forecast horizon in months: 3, 6, 12"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve time-series revenue and ARR forecast with upper & lower 95% confidence intervals."""
    return PredictiveService.get_revenue_forecast(db=db, horizon_months=horizon_months)


@router.get("/churn/accounts", response_model=CustomerChurnResponse)
def get_customer_churn_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve machine learning customer churn risk predictions, risk tiers, and recommended interventions."""
    return PredictiveService.get_churn_predictions(db=db)


@router.get("/models", response_model=List[MLModelRegistrySummary])
def list_ml_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List registered machine learning models and evaluation performance metrics (R2, RMSE, ROC-AUC)."""
    return PredictiveService.get_models(db=db)


@router.post("/models/{model_id}/retrain", response_model=RetrainModelResponse)
def retrain_ml_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Trigger on-demand training of an enterprise machine learning model with latest data."""
    return PredictiveService.retrain_model(db=db, model_id=model_id)
