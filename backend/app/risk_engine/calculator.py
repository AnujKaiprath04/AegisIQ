from datetime import datetime, timezone
from typing import Any, Dict, List
from app.risk_engine.types import (
    BusinessRiskItem,
    EnterpriseRiskScorecard,
    RiskPillar,
)


class CompositeRiskCalculator:
    """Bayesian Weighted Enterprise Composite Risk Aggregator."""

    PILLAR_WEIGHTS = {
        RiskPillar.CUSTOMER_LOSS: 0.30,
        RiskPillar.REVENUE_DECLINE: 0.25,
        RiskPillar.SUPPLY_CHAIN_DISRUPTION: 0.15,
        RiskPillar.LOW_PERFORMING_PRODUCT: 0.10,
        RiskPillar.FINANCIAL_ANOMALY: 0.10,
        RiskPillar.OPERATIONAL_BOTTLENECK: 0.10,
    }

    @classmethod
    def calculate_scorecard(cls, risk_items: List[BusinessRiskItem]) -> EnterpriseRiskScorecard:
        pillar_breakdown: Dict[str, float] = {}
        total_exposure = 0.0
        weighted_score = 0.0

        for pillar, weight in cls.PILLAR_WEIGHTS.items():
            matching = [r for r in risk_items if r.pillar == pillar]
            if matching:
                avg_score = sum(r.risk_score for r in matching) / len(matching)
                pillar_breakdown[pillar.value] = round(avg_score, 1)
                weighted_score += avg_score * weight
                total_exposure += sum(r.financial_exposure_usd for r in matching)
            else:
                pillar_breakdown[pillar.value] = 0.0

        composite_score = round(weighted_score, 1)

        if composite_score <= 20.0:
            status_str = "OPTIMAL_STABILITY (LOW_RISK)"
        elif composite_score <= 40.0:
            status_str = "CONTROLLED_LOW_RISK"
        elif composite_score <= 60.0:
            status_str = "MODERATE_ELEVATED_RISK"
        else:
            status_str = "CRITICAL_ACTION_REQUIRED"

        highest_risk = max(risk_items, key=lambda x: x.risk_score).title if risk_items else "None"
        now_str = datetime.now(timezone.utc).isoformat()

        return EnterpriseRiskScorecard(
            composite_risk_score=composite_score,
            risk_status=status_str,
            total_financial_exposure_usd=round(total_exposure, 2),
            pillar_breakdown=pillar_breakdown,
            active_risks_count=len(risk_items),
            highest_priority_risk=highest_risk,
            assessment_timestamp=now_str,
        )
