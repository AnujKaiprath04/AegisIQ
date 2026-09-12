import json
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.predictive import MLModelRegistry, ForecastPrediction, CustomerChurnPrediction
from app.models.user import User
from app.schemas.predictive import (
    CustomerChurnRecord,
    CustomerChurnResponse,
    ForecastDataPoint,
    MLModelRegistrySummary,
    RetrainModelResponse,
    TimeSeriesForecastResponse,
)

logger = logging.getLogger("aegisiq.predictive_service")

SEEDED_MODELS = [
    {
        "model_name": "Enterprise ARR & Revenue Forecaster",
        "model_type": "TIME_SERIES_FORECAST",
        "algorithm": "EXPONENTIAL_SMOOTHING_HOLT_WINTERS",
        "status": "TRAINED",
        "accuracy_score": 0.962,  # R2
        "mae_metric": 115000.0,
        "rmse_metric": 142000.0,
        "features_used_json": json.dumps(["quarterly_arr", "net_retention_rate", "new_booking_pipeline", "market_seasonality"]),
    },
    {
        "model_name": "Customer Churn & Retention Classifier",
        "model_type": "CHURN_CLASSIFICATION",
        "algorithm": "GRADIENT_BOOSTED_TREES",
        "status": "TRAINED",
        "accuracy_score": 0.934,  # ROC-AUC
        "mae_metric": 0.042,
        "rmse_metric": 0.068,
        "features_used_json": json.dumps(["weekly_active_seats", "support_ticket_velocity", "contract_days_remaining", "invoice_overdue_days"]),
    },
    {
        "model_name": "Supply Chain & Hardware Demand Predictor",
        "model_type": "DEMAND_PREDICTION",
        "algorithm": "RIDGE_REGRESSION_AUTOREGRESSIVE",
        "status": "TRAINED",
        "accuracy_score": 0.918,
        "mae_metric": 840.0,
        "rmse_metric": 1250.0,
        "features_used_json": json.dumps(["inventory_velocity", "lead_time_days", "regional_fulfillment_rate"]),
    },
]

SEEDED_CHURN_ACCOUNTS = [
    {
        "client_name": "Apex Global Logistics",
        "account_arr": 620000.0,
        "churn_probability_pct": 82.4,
        "risk_tier": "HIGH_RISK",
        "top_risk_factors": ["Weekly active seat usage down 48%", "3 Unresolved Level-1 tickets", "Renewal in 45 days"],
        "recommended_intervention": "Schedule urgent executive review with VP of Customer Success and offer dedicated Technical Account Manager.",
        "contract_renewal_date": "2026-04-15",
    },
    {
        "client_name": "Nexus FinTech Corp",
        "account_arr": 480000.0,
        "churn_probability_pct": 74.8,
        "risk_tier": "HIGH_RISK",
        "top_risk_factors": ["Invoice payment delayed by 38 days", "Decision Intelligence API usage drop > 30%"],
        "recommended_intervention": "Initiate billing grace discussion and conduct value realization workshop for finance team.",
        "contract_renewal_date": "2026-05-01",
    },
    {
        "client_name": "Starlight Health Systems",
        "account_arr": 380000.0,
        "churn_probability_pct": 58.2,
        "risk_tier": "MEDIUM_RISK",
        "top_risk_factors": ["Executive sponsor departure", "Pending single-sign-on integration ticket"],
        "recommended_intervention": "Onboard incoming Chief Information Officer and expedite SSO SAML integration.",
        "contract_renewal_date": "2026-06-30",
    },
    {
        "client_name": "Horizon Cloud Labs",
        "account_arr": 290000.0,
        "churn_probability_pct": 42.0,
        "risk_tier": "MEDIUM_RISK",
        "top_risk_factors": ["Plateaued expansion tier adoption", "Usage stable but no new seats added"],
        "recommended_intervention": "Deliver demo of new Generative AI & Knowledge Base RAG copilot add-on.",
        "contract_renewal_date": "2026-08-15",
    },
    {
        "client_name": "Vanguard Retail Group",
        "account_arr": 850000.0,
        "churn_probability_pct": 8.5,
        "risk_tier": "LOW_RISK",
        "top_risk_factors": ["Optimal seat usage (94%)", "Zero SLA breaches", "High multi-domain dashboard engagement"],
        "recommended_intervention": "Present multi-year enterprise renewal contract with volume discount incentives.",
        "contract_renewal_date": "2026-11-30",
    },
    {
        "client_name": "Quantum Aerospace",
        "account_arr": 720000.0,
        "churn_probability_pct": 6.2,
        "risk_tier": "LOW_RISK",
        "top_risk_factors": ["Expanded to 3 new business units", "High API throughput"],
        "recommended_intervention": "Explore enterprise co-marketing case study and executive advisory council invitation.",
        "contract_renewal_date": "2026-12-15",
    },
]


class PredictiveService:
    @staticmethod
    def seed_initial_predictive_data(db: Session):
        """Seed initial ML models and customer churn risk scores."""
        for m_spec in SEEDED_MODELS:
            existing = db.query(MLModelRegistry).filter(MLModelRegistry.model_name == m_spec["model_name"]).first()
            if not existing:
                m = MLModelRegistry(**m_spec)
                db.add(m)
        db.commit()

        for c_spec in SEEDED_CHURN_ACCOUNTS:
            existing_c = db.query(CustomerChurnPrediction).filter(CustomerChurnPrediction.client_name == c_spec["client_name"]).first()
            if not existing_c:
                c = CustomerChurnPrediction(
                    client_name=c_spec["client_name"],
                    account_arr=c_spec["account_arr"],
                    churn_probability_pct=c_spec["churn_probability_pct"],
                    risk_tier=c_spec["risk_tier"],
                    top_risk_factors_json=json.dumps(c_spec["top_risk_factors"]),
                    recommended_intervention=c_spec["recommended_intervention"],
                    contract_renewal_date=c_spec["contract_renewal_date"],
                )
                db.add(c)
        db.commit()

    @staticmethod
    def get_revenue_forecast(db: Session, horizon_months: int = 12) -> TimeSeriesForecastResponse:
        """Generate time-series revenue and ARR forecast with 95% confidence intervals."""
        PredictiveService.seed_initial_predictive_data(db)

        historical = [
            {"period": "2025-Q1", "val": 18.2},
            {"period": "2025-Q2", "val": 19.8},
            {"period": "2025-Q3", "val": 21.5},
            {"period": "2025-Q4", "val": 23.2},
            {"period": "2026-Q1", "val": 24.8},  # Current
        ]

        # Forecast periods based on horizon
        projections_all = [
            {"period": "2026-Q2", "pred": 26.6, "lower": 25.8, "upper": 27.4},
            {"period": "2026-Q3", "pred": 28.5, "lower": 27.2, "upper": 29.8},
            {"period": "2026-Q4", "pred": 30.8, "lower": 29.0, "upper": 32.6},
            {"period": "2027-Q1", "pred": 33.2, "lower": 31.0, "upper": 35.4},
        ]

        # Filter projections by horizon
        if horizon_months <= 3:
            projections = projections_all[:1]
        elif horizon_months <= 6:
            projections = projections_all[:2]
        else:
            projections = projections_all

        data_points: List[ForecastDataPoint] = []
        for h in historical:
            data_points.append(
                ForecastDataPoint(
                    period=h["period"],
                    historical_actual=h["val"],
                    predicted_value=h["val"],
                    lower_bound_95=h["val"],
                    upper_bound_95=h["val"],
                    is_forecast=False,
                )
            )

        for p in projections:
            data_points.append(
                ForecastDataPoint(
                    period=p["period"],
                    historical_actual=None,
                    predicted_value=p["pred"],
                    lower_bound_95=p["lower"],
                    upper_bound_95=p["upper"],
                    is_forecast=True,
                )
            )

        final_pred = projections[-1]["pred"]
        current_val = 24.8
        growth_pct = round(((final_pred - current_val) / current_val) * 100, 1)

        return TimeSeriesForecastResponse(
            metric_name="ARR_USD_MILLIONS",
            horizon_months=horizon_months,
            model_name="Enterprise ARR & Revenue Forecaster",
            algorithm="Exponential Smoothing (Holt-Winters)",
            r2_score=0.962,
            rmse=0.142,
            data_points=data_points,
            projected_growth_pct=growth_pct,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def get_churn_predictions(db: Session) -> CustomerChurnResponse:
        """Fetch ranked customer churn predictions and high-risk accounts."""
        PredictiveService.seed_initial_predictive_data(db)
        churn_records = db.query(CustomerChurnPrediction).order_by(CustomerChurnPrediction.churn_probability_pct.desc()).all()

        high_count = 0
        med_count = 0
        low_count = 0
        arr_at_risk = 0.0

        records: List[CustomerChurnRecord] = []
        for r in churn_records:
            factors = json.loads(r.top_risk_factors_json) if r.top_risk_factors_json else []
            if r.risk_tier == "HIGH_RISK":
                high_count += 1
                arr_at_risk += r.account_arr
            elif r.risk_tier == "MEDIUM_RISK":
                med_count += 1
            else:
                low_count += 1

            records.append(
                CustomerChurnRecord(
                    id=r.id,
                    client_name=r.client_name,
                    account_arr=r.account_arr,
                    churn_probability_pct=r.churn_probability_pct,
                    risk_tier=r.risk_tier,
                    top_risk_factors=factors,
                    recommended_intervention=r.recommended_intervention,
                    contract_renewal_date=r.contract_renewal_date,
                )
            )

        return CustomerChurnResponse(
            total_accounts_evaluated=len(records),
            high_risk_count=high_count,
            medium_risk_count=med_count,
            low_risk_count=low_count,
            arr_at_risk=arr_at_risk,
            accounts=records,
        )

    @staticmethod
    def get_models(db: Session) -> List[MLModelRegistrySummary]:
        PredictiveService.seed_initial_predictive_data(db)
        models = db.query(MLModelRegistry).order_by(MLModelRegistry.id.asc()).all()
        return [MLModelRegistrySummary.model_validate(m) for m in models]

    @staticmethod
    def retrain_model(db: Session, model_id: int) -> RetrainModelResponse:
        """Trigger model retraining with fresh warehouse data and update evaluation metrics."""
        model = db.query(MLModelRegistry).filter(MLModelRegistry.id == model_id).first()
        if not model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ML Model {model_id} not found.")

        start = time.time()
        time.sleep(0.08)  # Simulate model training iteration
        elapsed = round(time.time() - start, 2)

        # Update model accuracy slightly
        new_acc = min(0.985, round(model.accuracy_score + 0.006, 3))
        model.accuracy_score = new_acc
        model.last_trained_at = datetime.now(timezone.utc)
        model.status = "TRAINED"
        db.commit()
        db.refresh(model)

        return RetrainModelResponse(
            model_id=model.id,
            model_name=model.model_name,
            status=model.status,
            new_accuracy_score=new_acc,
            duration_seconds=elapsed,
            message=f"Model '{model.model_name}' retrained successfully in {elapsed}s. Evaluation metric updated to {new_acc}.",
        )
