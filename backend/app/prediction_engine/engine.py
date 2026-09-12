from typing import Any, Dict, List
from app.prediction_engine.types import ModelInfo, PredictionModelType

REGISTERED_PREDICTIVE_MODELS: List[ModelInfo] = [
    ModelInfo(
        model_id="pm-rev-01",
        name="Enterprise ARR Forecaster",
        type=PredictionModelType.REVENUE_FORECAST,
        algorithm="Holt-Winters Multiplicative Seasonality + ARIMA(2,1,2)",
        target_metric="R-Squared",
        accuracy_score=0.962,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-churn-02",
        name="Customer Churn Risk Classifier",
        type=PredictionModelType.CUSTOMER_CHURN,
        algorithm="XGBoost Classifier + SHAP TreeExplainer",
        target_metric="ROC-AUC",
        accuracy_score=0.942,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-sales-03",
        name="Multi-Region Sales Forecaster",
        type=PredictionModelType.SALES_FORECAST,
        algorithm="Exponential Smoothing with Trend Damping",
        target_metric="MAPE",
        accuracy_score=0.954,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-demand-04",
        name="SKU Demand & Peak Predictor",
        type=PredictionModelType.DEMAND_FORECAST,
        algorithm="Random Forest Regressor + Lag Decomposition",
        target_metric="R-Squared",
        accuracy_score=0.938,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-attrition-05",
        name="Workforce Turnover & Flight-Risk Model",
        type=PredictionModelType.EMPLOYEE_ATTRITION,
        algorithm="LightGBM Binary Classifier",
        target_metric="ROC-AUC",
        accuracy_score=0.916,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-inventory-06",
        name="Operations Research Inventory Optimizer",
        type=PredictionModelType.INVENTORY_OPTIMIZATION,
        algorithm="Deterministic EOQ & Stochastic Safety Stock Engine",
        target_metric="Service Level",
        accuracy_score=0.992,
        status="ACTIVE_PRODUCTION",
    ),
    ModelInfo(
        model_id="pm-clv-07",
        name="Customer Lifetime Value Forecaster",
        type=PredictionModelType.CUSTOMER_LTV,
        algorithm="Probabilistic BG/NBD + Gamma-Gamma DCF",
        target_metric="Variance Explained",
        accuracy_score=0.948,
        status="ACTIVE_PRODUCTION",
    ),
]


class PredictiveAnalyticsEngine:
    """Master Predictive Analytics Engine managing models and inference workflows."""

    @classmethod
    def list_models(cls) -> List[ModelInfo]:
        return REGISTERED_PREDICTIVE_MODELS
