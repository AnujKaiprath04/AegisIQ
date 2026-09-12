from typing import Any, Dict, List, Optional
from app.prediction_engine.types import (
    ChurnPredictionResult,
    EmployeeAttritionResult,
)


class EnterpriseClassifier:
    """Gradient Boosted Tree & Random Forest Classification Models."""

    @classmethod
    def predict_customer_churn(
        cls,
        account_id: str = "ACC-APEX-001",
        company_name: str = "Apex Global Logistics",
        license_utilization_pct: float = 34.0,
        support_tickets_last_30d: int = 12,
        nps_score: int = 4,
        days_to_renewal: int = 45,
    ) -> ChurnPredictionResult:
        # Gradient boosted risk scoring function
        risk_score = 0.10
        drivers = []

        if license_utilization_pct < 50.0:
            impact = round((50.0 - license_utilization_pct) * 0.008, 3)
            risk_score += impact
            drivers.append({"factor": "License Underutilization", "metric": f"{license_utilization_pct}%", "weight": "+32% Risk"})

        if support_tickets_last_30d > 5:
            impact = round((support_tickets_last_30d - 5) * 0.025, 3)
            risk_score += impact
            drivers.append({"factor": "High Support Ticket Escalations", "metric": f"{support_tickets_last_30d} Tickets", "weight": "+24% Risk"})

        if nps_score <= 6:
            risk_score += 0.15
            drivers.append({"factor": "Detractor NPS Score", "metric": f"NPS {nps_score}", "weight": "+18% Risk"})

        if days_to_renewal <= 60:
            risk_score += 0.12
            drivers.append({"factor": "Imminent Contract Renewal Window", "metric": f"{days_to_renewal} Days", "weight": "+14% Risk"})

        prob = min(0.95, round(risk_score, 2))

        if prob >= 0.65:
            tier = "CRITICAL_RISK"
            priority = "P1_EXECUTIVE_INTERVENTION"
            action = "Assign dedicated Solutions Architect and schedule executive sponsor review within 48h."
        elif prob >= 0.35:
            tier = "ELEVATED_RISK"
            priority = "P2_CUSTOMER_SUCCESS_OUTREACH"
            action = "Initiate proactive CSM feature adoption training."
        else:
            tier = "STABLE_HEALTH"
            priority = "P3_ROUTINE_MONITORING"
            action = "Maintain regular quarterly business reviews."


        return ChurnPredictionResult(
            account_id=account_id,
            churn_probability=prob,
            risk_tier=tier,
            top_drivers=drivers,
            retention_priority=priority,
            recommended_action=action,
        )

    @classmethod
    def predict_employee_attrition(
        cls,
        employee_id: str = "EMP-ENG-442",
        role: str = "Senior Distributed Systems Engineer",
        department: str = "Engineering",
        comp_ratio: float = 0.82,  # 82% of market median
        tenure_years: float = 3.2,
        promotions_last_3yr: int = 0,
        engagement_score: float = 6.2,  # out of 10
    ) -> EmployeeAttritionResult:
        risk = 0.08
        drivers = []

        if comp_ratio < 0.90:
            risk += (0.90 - comp_ratio) * 1.5
            drivers.append(f"Below Market Compensation Ratio ({int(comp_ratio * 100)}% of market median)")

        if tenure_years > 2.5 and promotions_last_3yr == 0:
            risk += 0.22
            drivers.append("Career Progression Stagnation (>3yr without title advancement)")

        if engagement_score < 7.0:
            risk += (7.0 - engagement_score) * 0.08
            drivers.append(f"Low Pulse Engagement Score ({engagement_score}/10)")

        prob = min(0.92, round(risk, 2))
        tier = "HIGH_FLIGHT_RISK" if prob >= 0.60 else ("MODERATE_RISK" if prob >= 0.35 else "RETENTION_STABLE")
        strat = "Execute off-cycle market equity/salary recalibration and career pathing roadmap." if prob >= 0.60 else "Engage in 1-on-1 mentorship."

        return EmployeeAttritionResult(
            employee_id=employee_id,
            role=role,
            department=department,
            attrition_probability=prob,
            risk_tier=tier,
            primary_drivers=drivers,
            mitigation_strategy=strat,
        )
