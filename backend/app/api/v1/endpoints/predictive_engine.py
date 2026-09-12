from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.predictive_engine import (
    CustomerChurnRequestSchema,
    CustomerChurnResponseSchema,
    CustomerLTVRequestSchema,
    CustomerLTVResponseSchema,
    DemandForecastRequestSchema,
    DemandForecastResponseSchema,
    EmployeeAttritionRequestSchema,
    EmployeeAttritionResponseSchema,
    InventoryOptimizationRequestSchema,
    InventoryOptimizationResponseSchema,
    ModelInfoSchema,
    PredictiveModelListResponse,
    RevenueForecastRequestSchema,
    RevenueForecastResponseSchema,
)
from app.prediction_engine.forecaster import EnterpriseForecaster
from app.prediction_engine.classifier import EnterpriseClassifier
from app.prediction_engine.optimizer import InventoryOptimizer
from app.prediction_engine.clv_calculator import CustomerLTVCalculator
from app.prediction_engine.engine import PredictiveAnalyticsEngine

router = APIRouter(prefix="/ml/predictions", tags=["Part 3 - Module 3: Predictive Analytics Engine"])


@router.post("/revenue-forecast", response_model=RevenueForecastResponseSchema)
def forecast_enterprise_revenue(
    req: RevenueForecastRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Forecast enterprise ARR & revenue using Holt-Winters Multiplicative Seasonality & ARIMA Ensemble."""
    result = EnterpriseForecaster.forecast_revenue(
        historical_baseline_arr=req.historical_baseline_arr,
        horizon_quarters=req.horizon_quarters,
    )
    return RevenueForecastResponseSchema(**result.model_dump())


@router.post("/customer-churn", response_model=CustomerChurnResponseSchema)
def predict_customer_churn(
    req: CustomerChurnRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Predict individual account churn probability, risk decile, and primary churn drivers."""
    result = EnterpriseClassifier.predict_customer_churn(
        account_id=req.account_id,
        company_name=req.company_name,
        license_utilization_pct=req.license_utilization_pct,
        support_tickets_last_30d=req.support_tickets_last_30d,
        nps_score=req.nps_score,
        days_to_renewal=req.days_to_renewal,
    )
    return CustomerChurnResponseSchema(**result.model_dump())


@router.post("/demand-forecast", response_model=DemandForecastResponseSchema)
def forecast_sku_demand(
    req: DemandForecastRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Forecast forward SKU demand curves with seasonal peak detection and stockout warnings."""
    result = EnterpriseForecaster.forecast_demand(
        sku_id=req.sku_id,
        product_name=req.product_name,
        horizon_months=req.horizon_months,
    )
    return DemandForecastResponseSchema(**result.model_dump())


@router.post("/employee-attrition", response_model=EmployeeAttritionResponseSchema)
def predict_employee_attrition(
    req: EmployeeAttritionRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Evaluate workforce flight-risk, tenure stagnation, compensation parity, and retention roadmaps."""
    result = EnterpriseClassifier.predict_employee_attrition(
        employee_id=req.employee_id,
        role=req.role,
        department=req.department,
        comp_ratio=req.comp_ratio,
        tenure_years=req.tenure_years,
        promotions_last_3yr=req.promotions_last_3yr,
        engagement_score=req.engagement_score,
    )
    return EmployeeAttritionResponseSchema(**result.model_dump())


@router.post("/inventory-optimization", response_model=InventoryOptimizationResponseSchema)
def optimize_inventory(
    req: InventoryOptimizationRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Calculate Economic Order Quantity (EOQ), Safety Stock, and Reorder Point (ROP) thresholds."""
    result = InventoryOptimizer.optimize(
        sku_id=req.sku_id,
        product_name=req.product_name,
        annual_demand_units=req.annual_demand_units,
        order_cost_usd=req.order_cost_usd,
        unit_holding_cost_usd=req.unit_holding_cost_usd,
        lead_time_days=req.lead_time_days,
        daily_demand_std_dev=req.daily_demand_std_dev,
        service_level=req.service_level,
    )
    return InventoryOptimizationResponseSchema(**result.model_dump())


@router.post("/customer-ltv", response_model=CustomerLTVResponseSchema)
def calculate_customer_lifetime_value(
    req: CustomerLTVRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Calculate discounted customer lifetime value (CLV) and strategic tier segmentation."""
    result = CustomerLTVCalculator.calculate_clv(
        account_id=req.account_id,
        company_name=req.company_name,
        monthly_revenue_usd=req.monthly_revenue_usd,
        gross_margin_pct=req.gross_margin_pct,
        monthly_churn_rate=req.monthly_churn_rate,
        annual_discount_rate=req.annual_discount_rate,
    )
    return CustomerLTVResponseSchema(**result.model_dump())


@router.get("/models", response_model=PredictiveModelListResponse)
def list_predictive_models(
    current_user: User = Depends(get_current_user),
):
    """List all 7 registered enterprise predictive models with operational performance metrics."""
    models = PredictiveAnalyticsEngine.list_models()
    return PredictiveModelListResponse(
        total_models=len(models),
        models=[ModelInfoSchema(**m.model_dump()) for m in models],
    )
