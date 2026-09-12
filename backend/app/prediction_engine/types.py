from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictionModelType(str, Enum):
    REVENUE_FORECAST = "REVENUE_FORECAST"
    SALES_FORECAST = "SALES_FORECAST"
    CUSTOMER_CHURN = "CUSTOMER_CHURN"
    DEMAND_FORECAST = "DEMAND_FORECAST"
    EMPLOYEE_ATTRITION = "EMPLOYEE_ATTRITION"
    INVENTORY_OPTIMIZATION = "INVENTORY_OPTIMIZATION"
    CUSTOMER_LTV = "CUSTOMER_LTV"


class ForecastPoint(BaseModel):
    period: str
    predicted_value: float
    lower_bound_95: float
    upper_bound_95: float


class RevenueForecastResult(BaseModel):
    historical_baseline_arr: float
    forecast_points: List[ForecastPoint] = []
    projected_growth_rate: float
    metrics: Dict[str, Any] = {}


class ChurnPredictionResult(BaseModel):
    account_id: str
    churn_probability: float
    risk_tier: str
    top_drivers: List[Dict[str, Any]] = []
    retention_priority: str
    recommended_action: str


class DemandForecastResult(BaseModel):
    sku_id: str
    product_name: str
    forecast_units: List[ForecastPoint] = []
    peak_demand_period: str
    stockout_risk_level: str


class EmployeeAttritionResult(BaseModel):
    employee_id: str
    role: str
    department: str
    attrition_probability: float
    risk_tier: str
    primary_drivers: List[str] = []
    mitigation_strategy: str


class InventoryOptimizationResult(BaseModel):
    sku_id: str
    product_name: str
    economic_order_quantity_units: int
    safety_stock_units: int
    reorder_point_units: int
    estimated_annual_holding_cost_usd: float
    service_level_achieved: float


class CustomerLTVResult(BaseModel):
    account_id: str
    company_name: str
    predicted_lifetime_months: int
    expected_margin_usd: float
    net_present_clv_usd: float
    customer_tier: str


class ModelInfo(BaseModel):
    model_id: str
    name: str
    type: PredictionModelType
    algorithm: str
    target_metric: str
    accuracy_score: float
    status: str
