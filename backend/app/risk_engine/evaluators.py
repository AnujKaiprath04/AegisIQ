import time
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.risk_engine.types import (
    BusinessRiskItem,
    RiskPillar,
    RiskPriority,
    RiskTrend,
)


class DomainRiskEvaluator:
    """Evaluates business signals across individual enterprise risk pillars."""

    @classmethod
    def evaluate_revenue_decline(
        cls,
        current_arr: float = 24800000.0,
        yoy_growth_rate: float = 0.184,
        macro_volatility_factor: float = 0.05,
    ) -> BusinessRiskItem:
        # Downside vulnerability scoring
        exposure = current_arr * macro_volatility_factor
        score = 8.0  # Stable low risk
        now_str = datetime.now(timezone.utc).isoformat()

        return BusinessRiskItem(
            risk_id=f"risk-rev-{int(time.time())}",
            pillar=RiskPillar.REVENUE_DECLINE,
            title="Macroeconomic Downside Revenue Sensitivity",
            description="Stress test of macro volatility indicates bounded downside ARR vulnerability under adverse market conditions.",
            risk_score=score,
            priority_level=RiskPriority.LOW,
            financial_exposure_usd=round(exposure, 2),
            likelihood_score=2,
            impact_score=2,
            mitigation_actions=[
                "Maintain diversified client acquisition across non-correlated sectors.",
                "Incentivize 2-year upfront commitments with multi-year pricing protection.",
            ],
            trend=RiskTrend.STABLE,
            last_assessed_at=now_str,
        )

    @classmethod
    def evaluate_customer_loss(
        cls,
        accounts_at_risk_arr: float = 480000.0,
        top_5_concentration_pct: float = 28.0,
    ) -> BusinessRiskItem:
        score = 18.0
        now_str = datetime.now(timezone.utc).isoformat()

        return BusinessRiskItem(
            risk_id=f"risk-cust-{int(time.time())}",
            pillar=RiskPillar.CUSTOMER_LOSS,
            title="Tier-1 Enterprise Account Churn Concentration",
            description=f"Apex Global Logistics ($480k ARR) exhibits critical churn signals. Top 5 accounts comprise {top_5_concentration_pct}% of total ARR.",
            risk_score=score,
            priority_level=RiskPriority.MEDIUM,
            financial_exposure_usd=accounts_at_risk_arr,
            likelihood_score=3,
            impact_score=4,
            mitigation_actions=[
                "Execute Module 4 Executive Retention Playbook for Apex Global Logistics.",
                "Implement proactive CSM quarterly feature utilization audits.",
            ],
            trend=RiskTrend.DECREASING,
            last_assessed_at=now_str,
        )

    @classmethod
    def evaluate_supply_chain(
        cls,
        max_lead_time_days: int = 28,
        single_source_components: int = 2,
    ) -> BusinessRiskItem:
        score = 16.0
        exposure = 110000.0
        now_str = datetime.now(timezone.utc).isoformat()

        return BusinessRiskItem(
            risk_id=f"risk-sc-{int(time.time())}",
            pillar=RiskPillar.SUPPLY_CHAIN_DISRUPTION,
            title="Single-Source ASIC Chipset Lead-Time Vulnerability",
            description=f"Primary semiconductor supplier indicates {max_lead_time_days}-day lead time on critical Fiber Switch ASICs.",
            risk_score=score,
            priority_level=RiskPriority.MEDIUM,
            financial_exposure_usd=exposure,
            likelihood_score=3,
            impact_score=3,
            mitigation_actions=[
                "Qualify secondary semiconductor fabricator in Taiwan region.",
                "Maintain 45-day safety stock buffer calculated by Module 3 Inventory Optimizer.",
            ],
            trend=RiskTrend.STABLE,
            last_assessed_at=now_str,
        )
