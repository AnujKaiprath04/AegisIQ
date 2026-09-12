from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class KPIMetricResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    description: Optional[str] = None
    formula_expression: Optional[str] = None
    unit: str
    current_value: float
    target_value: float
    benchmark_value: Optional[float] = None
    variance_pct: float
    trend_direction: str
    status: str  # ON_TRACK, WARNING, CRITICAL
    period: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KPITargetUpdate(BaseModel):
    target_value: float = Field(..., gt=0)
    period: Optional[str] = None


class KPICalculateRequest(BaseModel):
    formula_type: str = Field(..., description="GROSS_MARGIN, CAC, LTV_CAC, QUICK_RATIO, INVENTORY_TURNOVER, CHURN_RATE, EBITDA_MARGIN")
    parameters: dict = Field(default_factory=dict)


class KPICalculateResponse(BaseModel):
    formula_type: str
    name: str
    calculated_value: float
    formatted_value: str
    unit: str
    status: str
    interpretation: str
    inputs_used: dict
