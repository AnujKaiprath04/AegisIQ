from typing import Any, Dict, List, Optional
from app.xai_studio.types import (
    CounterfactualScenario,
    GlobalFeatureRanking,
    ModelTransparencyCard,
    XAIExplanationResult,
)
from app.xai_studio.shap_explainer import ShapAttributionEngine
from app.xai_studio.lime_explainer import LimeSurrogateEngine
from app.xai_studio.counterfactual_engine import CounterfactualSimulator
from app.xai_studio.narrator import XAINarrativeSynthesizer

GLOBAL_FEATURE_IMPORTANCE_REGISTRY: Dict[str, List[GlobalFeatureRanking]] = {
    "customer_churn_xgboost": [
        GlobalFeatureRanking(feature_name="monthly_support_tickets", importance_score=0.342, rank=1, domain="Customer Service"),
        GlobalFeatureRanking(feature_name="csm_nps_score", importance_score=0.264, rank=2, domain="Account Health"),
        GlobalFeatureRanking(feature_name="monthly_active_users", importance_score=0.185, rank=3, domain="Product Adoption"),
        GlobalFeatureRanking(feature_name="contract_tenure_months", importance_score=0.118, rank=4, domain="Commercial Contract"),
        GlobalFeatureRanking(feature_name="arr_usd", importance_score=0.091, rank=5, domain="Financial"),
    ],
    "revenue_forecast_arima": [
        GlobalFeatureRanking(feature_name="historical_arr_lag_12m", importance_score=0.410, rank=1, domain="Financial History"),
        GlobalFeatureRanking(feature_name="quarterly_seasonality_index", importance_score=0.285, rank=2, domain="Macro Seasonality"),
        GlobalFeatureRanking(feature_name="pipeline_coverage_ratio", importance_score=0.195, rank=3, domain="Sales Pipeline"),
        GlobalFeatureRanking(feature_name="macro_gdp_growth", importance_score=0.110, rank=4, domain="Macroeconomic"),
    ],
}

MODEL_TRANSPARENCY_REGISTRY: Dict[str, ModelTransparencyCard] = {
    "customer_churn_xgboost": ModelTransparencyCard(
        model_id="customer_churn_xgboost",
        model_name="Enterprise Customer Churn Gradient Boosted Tree",
        version="v2.4.1",
        task_type="Binary Classification",
        training_records_count=24800,
        disparate_impact_ratio=1.04,
        demographic_parity_diff=0.02,
        compliance_status="AUDITED_COMPLIANT (EU AI Act & DORA Tier-1)",
        governance_notes="Model trained on anonymized enterprise metadata. Zero demographic or protected attributes used in inference tree.",
    ),
    "revenue_forecast_arima": ModelTransparencyCard(
        model_id="revenue_forecast_arima",
        model_name="Multiplicative Holt-Winters & ARIMA Revenue Forecaster",
        version="v1.8.0",
        task_type="Time-Series Forecasting",
        training_records_count=120,
        disparate_impact_ratio=1.00,
        demographic_parity_diff=0.00,
        compliance_status="AUDITED_COMPLIANT",
        governance_notes="Deterministic operations research statistical model with 95% confidence intervals.",
    ),
}


class EnterpriseXAIStudioEngine:
    """Master Explainable AI (XAI) Studio Engine."""

    @classmethod
    def explain_prediction(
        cls,
        model_id: str,
        input_features: Dict[str, Any],
        probability: float = 0.74,
    ) -> XAIExplanationResult:
        base_val = 0.22
        shap_vals = ShapAttributionEngine.explain(input_features, base_value=base_val)
        lime_vals = LimeSurrogateEngine.explain(input_features)
        narrative = XAINarrativeSynthesizer.synthesize(
            model_name=model_id.replace("_", " ").title(),
            probability=probability,
            shap_values=shap_vals,
        )

        label = "HIGH_CHURN_RISK" if probability >= 0.5 else "LOW_CHURN_RISK"

        return XAIExplanationResult(
            model_id=model_id,
            prediction_label=label,
            prediction_probability=probability,
            base_value=base_val,
            shap_values=shap_vals,
            lime_values=lime_vals,
            natural_language_explanation=narrative,
            confidence_score=0.95,
        )

    @classmethod
    def simulate_counterfactual(
        cls,
        model_id: str,
        input_features: Dict[str, Any],
        current_probability: float = 0.74,
        target_probability: float = 0.18,
    ) -> CounterfactualScenario:
        return CounterfactualSimulator.simulate(
            features=input_features,
            current_probability=current_probability,
            target_probability=target_probability,
        )

    @classmethod
    def get_global_feature_importance(cls, model_id: str) -> List[GlobalFeatureRanking]:
        return GLOBAL_FEATURE_IMPORTANCE_REGISTRY.get(
            model_id,
            GLOBAL_FEATURE_IMPORTANCE_REGISTRY["customer_churn_xgboost"],
        )

    @classmethod
    def get_model_transparency(cls, model_id: str) -> ModelTransparencyCard:
        return MODEL_TRANSPARENCY_REGISTRY.get(
            model_id,
            MODEL_TRANSPARENCY_REGISTRY["customer_churn_xgboost"],
        )
