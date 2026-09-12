from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.mlops_registry.types import (
    DriftMetric,
    FrameworkType,
    ModelStage,
    ModelVersion,
    RegisteredModel,
    RetrainingJob,
)
from app.mlops_registry.drift_monitor import DriftMonitorEngine
from app.mlops_registry.retraining_pipeline import AutomatedRetrainingPipeline
from app.mlops_registry.deployment_manager import CanaryDeploymentManager

SEEDED_REGISTERED_MODELS: List[RegisteredModel] = [
    RegisteredModel(
        model_id="customer_churn_xgboost",
        model_name="Customer Churn Gradient Boosted Risk Classifier",
        description="Predicts individual account churn probability and risk deciles based on usage and sentiment metrics.",
        framework=FrameworkType.XGBOOST,
        active_version="v2.4.1",
        all_versions=[
            ModelVersion(
                version_id="ver-churn-241",
                version_str="v2.4.1",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="ROC-AUC",
                accuracy_score=0.942,
                created_at="2026-08-30T12:00:00Z",
                deployed_at="2026-08-30T14:00:00Z",
            ),
            ModelVersion(
                version_id="ver-churn-250",
                version_str="v2.5.0-rc1",
                stage=ModelStage.CANARY,
                accuracy_metric_name="ROC-AUC",
                accuracy_score=0.951,
                created_at="2026-08-31T06:00:00Z",
                deployed_at="2026-08-31T06:10:00Z",
            ),
        ],
        canary_traffic_split_pct=10.0,
        last_retrained_at="2026-08-31T06:00:00Z",
    ),
    RegisteredModel(
        model_id="revenue_forecast_arima",
        model_name="Multiplicative Holt-Winters & ARIMA Revenue Forecaster",
        description="Multi-period time-series revenue and ARR forecasting with 95% confidence intervals.",
        framework=FrameworkType.ARIMA_STATS,
        active_version="v1.8.0",
        all_versions=[
            ModelVersion(
                version_id="ver-rev-180",
                version_str="v1.8.0",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="R-Squared",
                accuracy_score=0.962,
                created_at="2026-08-28T09:00:00Z",
                deployed_at="2026-08-28T09:30:00Z",
            ),
        ],
        canary_traffic_split_pct=0.0,
        last_retrained_at="2026-08-28T09:00:00Z",
    ),
    RegisteredModel(
        model_id="employee_attrition_gbt",
        model_name="Workforce Turnover & Talent Flight Risk Model",
        description="Evaluates employee retention risk against compensation parity and tenure stagnation.",
        framework=FrameworkType.XGBOOST,
        active_version="v1.5.2",
        all_versions=[
            ModelVersion(
                version_id="ver-attr-152",
                version_str="v1.5.2",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="ROC-AUC",
                accuracy_score=0.916,
                created_at="2026-08-29T10:00:00Z",
                deployed_at="2026-08-29T10:15:00Z",
            ),
        ],
        canary_traffic_split_pct=0.0,
        last_retrained_at="2026-08-29T10:00:00Z",
    ),
    RegisteredModel(
        model_id="sku_demand_forecaster",
        model_name="SKU Demand & Peak Consumption Forecaster",
        description="Projects forward product/inventory unit demand curves.",
        framework=FrameworkType.SCIKIT_LEARN,
        active_version="v2.1.0",
        all_versions=[
            ModelVersion(
                version_id="ver-dem-210",
                version_str="v2.1.0",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="MAPE",
                accuracy_score=0.062,
                created_at="2026-08-29T14:00:00Z",
                deployed_at="2026-08-29T14:30:00Z",
            ),
        ],
        canary_traffic_split_pct=0.0,
        last_retrained_at="2026-08-29T14:00:00Z",
    ),
    RegisteredModel(
        model_id="inventory_optimizer_eoq",
        model_name="Deterministic Wilson Economic Order Quantity & Safety Stock",
        description="Operations research inventory optimization model.",
        framework=FrameworkType.OPERATIONS_RESEARCH,
        active_version="v1.2.0",
        all_versions=[
            ModelVersion(
                version_id="ver-eoq-120",
                version_str="v1.2.0",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="Service Level",
                accuracy_score=0.975,
                created_at="2026-08-27T08:00:00Z",
                deployed_at="2026-08-27T08:00:00Z",
            ),
        ],
        canary_traffic_split_pct=0.0,
        last_retrained_at="2026-08-27T08:00:00Z",
    ),
    RegisteredModel(
        model_id="isolation_forest_anomalies",
        model_name="Unsupervised Tree Partition Outlier Isolation Model",
        description="Multi-dimensional anomaly detection for system and telemetry logs.",
        framework=FrameworkType.SCIKIT_LEARN,
        active_version="v3.0.0",
        all_versions=[
            ModelVersion(
                version_id="ver-if-300",
                version_str="v3.0.0",
                stage=ModelStage.PRODUCTION,
                accuracy_metric_name="Precision@k",
                accuracy_score=0.934,
                created_at="2026-08-30T16:00:00Z",
                deployed_at="2026-08-30T16:10:00Z",
            ),
        ],
        canary_traffic_split_pct=0.0,
        last_retrained_at="2026-08-30T16:00:00Z",
    ),
]


class EnterpriseMLOpsRegistry:
    """Master MLOps Model Versioning and Governance Registry."""

    _models: Dict[str, RegisteredModel] = {m.model_id: m for m in SEEDED_REGISTERED_MODELS}

    @classmethod
    def list_models(cls) -> List[RegisteredModel]:
        return list(cls._models.values())

    @classmethod
    def get_model(cls, model_id: str) -> RegisteredModel:
        model = cls._models.get(model_id)
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{model_id}' not found.")
        return model

    @classmethod
    def trigger_retraining(cls, model_id: str, triggered_by: str) -> RetrainingJob:
        model = cls.get_model(model_id)
        job = AutomatedRetrainingPipeline.execute_retraining(model_id, triggered_by=triggered_by)
        model.last_retrained_at = job.completed_at
        return job

    @classmethod
    def get_drift_metrics(cls, model_id: str) -> List[DriftMetric]:
        cls.get_model(model_id)
        return DriftMonitorEngine.evaluate_feature_drift(model_id)

    @classmethod
    def deploy_canary(cls, model_id: str, split_pct: float) -> RegisteredModel:
        model = cls.get_model(model_id)
        return CanaryDeploymentManager.set_canary(model, split_pct)

    @classmethod
    def promote_model(cls, model_id: str, version_str: str) -> RegisteredModel:
        model = cls.get_model(model_id)
        return CanaryDeploymentManager.promote_to_production(model, version_str)
