from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prediction_engine.types import (
    CustomerLTVResult,
    DemandForecastResult,
    EmployeeAttritionResult,
    ForecastPoint,
    InventoryOptimizationResult,
    ModelInfo,
    RevenueForecastResult,
)


class RevenueForecastRequestSchema(BaseModel):
    historical_baseline_arr: float = Field(default=24800000.0, ge=1000.0)
    horizon_quarters: int = Field(default=4, ge=1, le=12)


class RevenueForecastResponseSchema(RevenueForecastResult):
    pass


class CustomerChurnRequestSchema(BaseModel):
    account_id: str = "ACC-APEX-001"
    company_name: str = "Apex Global Logistics"
    license_utilization_pct: float = Field(default=34.0, ge=0.0, le=100.0)
    support_tickets_last_30d: int = Field(default=12, ge=0)
    nps_score: int = Field(default=4, ge=0, le=10)
    days_to_renewal: int = Field(default=45, ge=1)


class CustomerChurnResponseSchema(BaseModel):
    account_id: str
    churn_probability: float
    risk_tier: str
    top_drivers: List[Dict[str, Any]] = []
    retention_priority: str
    recommended_action: str


class DemandForecastRequestSchema(BaseModel):
    sku_id: str = "SKU-ENT-SERVER-01"
    product_name: str = "Enterprise Cloud Blade 128G"
    horizon_months: int = Field(default=6, ge=1, le=24)


class DemandForecastResponseSchema(DemandForecastResult):
    pass


class EmployeeAttritionRequestSchema(BaseModel):
    employee_id: str = "EMP-ENG-442"
    role: str = "Senior Distributed Systems Engineer"
    department: str = "Engineering"
    comp_ratio: float = Field(default=0.82, ge=0.1, le=3.0)
    tenure_years: float = Field(default=3.2, ge=0.0)
    promotions_last_3yr: int = Field(default=0, ge=0)
    engagement_score: float = Field(default=6.2, ge=0.0, le=10.0)


class EmployeeAttritionResponseSchema(EmployeeAttritionResult):
    pass


class InventoryOptimizationRequestSchema(BaseModel):
    sku_id: str = "SKU-OPT-100"
    product_name: str = "Enterprise Fiber Switch 48-Port"
    annual_demand_units: int = Field(default=12000, ge=1)
    order_cost_usd: float = Field(default=250.0, ge=0.0)
    unit_holding_cost_usd: float = Field(default=45.0, ge=0.01)
    lead_time_days: int = Field(default=14, ge=1)
    daily_demand_std_dev: float = Field(default=8.5, ge=0.0)
    service_level: float = Field(default=0.95, ge=0.5, le=0.999)


class InventoryOptimizationResponseSchema(InventoryOptimizationResult):
    pass


class CustomerLTVRequestSchema(BaseModel):
    account_id: str = "ACC-NEXUS-002"
    company_name: str = "Nexus FinTech Labs"
    monthly_revenue_usd: float = Field(default=25000.0, ge=100.0)
    gross_margin_pct: float = Field(default=0.684, ge=0.01, le=1.0)
    monthly_churn_rate: float = Field(default=0.015, ge=0.0001, le=1.0)
    annual_discount_rate: float = Field(default=0.08, ge=0.0, le=0.5)


class CustomerLTVResponseSchema(CustomerLTVResult):
    pass


class ModelInfoSchema(ModelInfo):
    pass


class PredictiveModelListResponse(BaseModel):
    total_models: int
    models: List[ModelInfoSchema] = []
