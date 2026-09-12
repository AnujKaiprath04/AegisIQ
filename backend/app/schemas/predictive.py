from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ForecastDataPoint(BaseModel):
    period: str
    historical_actual: Optional[float] = None
    predicted_value: Optional[float] = None
    lower_bound_95: Optional[float] = None
    upper_bound_95: Optional[float] = None
    is_forecast: bool = False


class TimeSeriesForecastResponse(BaseModel):
    metric_name: str
    horizon_months: int
    model_name: str
    algorithm: str
    r2_score: float
    rmse: float
    data_points: List[ForecastDataPoint] = []
    projected_growth_pct: float
    generated_at: datetime


class CustomerChurnRecord(BaseModel):
    id: int
    client_name: str
    account_arr: float
    churn_probability_pct: float
    risk_tier: str  # LOW_RISK, MEDIUM_RISK, HIGH_RISK
    top_risk_factors: List[str] = []
    recommended_intervention: str
    contract_renewal_date: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerChurnResponse(BaseModel):
    total_accounts_evaluated: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    arr_at_risk: float
    accounts: List[CustomerChurnRecord] = []


class MLModelRegistrySummary(BaseModel):
    id: int
    model_name: str
    model_type: str
    algorithm: str
    status: str
    accuracy_score: float
    mae_metric: float
    rmse_metric: float
    last_trained_at: datetime

    class Config:
        from_attributes = True


class RetrainModelResponse(BaseModel):
    model_id: int
    model_name: str
    status: str
    new_accuracy_score: float
    duration_seconds: float
    message: str
