from typing import Any, Dict, List, Optional
from app.risk_engine.types import (
    BusinessRiskItem,
    EnterpriseRiskScorecard,
    RiskHeatmapPoint,
    RiskPillar,
    RiskPriority,
    RiskTrend,
)
from app.risk_engine.evaluators import DomainRiskEvaluator
from app.risk_engine.calculator import CompositeRiskCalculator

SEEDED_RISK_ITEMS: List[BusinessRiskItem] = [
    BusinessRiskItem(
        risk_id="risk-rev-001",
        pillar=RiskPillar.REVENUE_DECLINE,
        title="Macroeconomic Downside Revenue Sensitivity",
        description="Stress testing across volatile interest rate regimes indicates bounded downside ARR vulnerability under adverse market conditions.",
        risk_score=8.0,
        priority_level=RiskPriority.LOW,
        financial_exposure_usd=320000.0,
        likelihood_score=2,
        impact_score=2,
        mitigation_actions=[
            "Maintain diversified client acquisition across non-correlated enterprise sectors.",
            "Incentivize 2-year upfront commitments with multi-year pricing protection.",
        ],
        trend=RiskTrend.STABLE,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
    BusinessRiskItem(
        risk_id="risk-cust-002",
        pillar=RiskPillar.CUSTOMER_LOSS,
        title="Tier-1 Enterprise Account Churn Concentration",
        description="Apex Global Logistics ($480k ARR) exhibits critical churn signals. Top 5 accounts comprise 28% of total ARR.",
        risk_score=18.0,
        priority_level=RiskPriority.MEDIUM,
        financial_exposure_usd=480000.0,
        likelihood_score=3,
        impact_score=4,
        mitigation_actions=[
            "Execute Module 4 Executive Retention Playbook for Apex Global Logistics.",
            "Deploy dedicated Senior Solutions Architect to audit license utilization bottlenecks.",
        ],
        trend=RiskTrend.DECREASING,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
    BusinessRiskItem(
        risk_id="risk-prod-003",
        pillar=RiskPillar.LOW_PERFORMING_PRODUCT,
        title="Legacy On-Premise Connectors Margin Erosion",
        description="Legacy v1 connectors record 12% lower gross margin (56.4%) and high ongoing maintenance overhead.",
        risk_score=14.0,
        priority_level=RiskPriority.LOW,
        financial_exposure_usd=65000.0,
        likelihood_score=2,
        impact_score=3,
        mitigation_actions=[
            "Sunset v1 connectors with 6-month deprecation grace period.",
            "Offer automated migration tooling to zero-trust cloud connectors.",
        ],
        trend=RiskTrend.DECREASING,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
    BusinessRiskItem(
        risk_id="risk-ops-004",
        pillar=RiskPillar.OPERATIONAL_BOTTLENECK,
        title="Peak 06:00 UTC Database Pool Saturation",
        description="Simultaneous enterprise ETL ingestion jobs cause 82% connection pool utilization on primary PostgreSQL cluster.",
        risk_score=6.0,
        priority_level=RiskPriority.MINIMAL,
        financial_exposure_usd=15000.0,
        likelihood_score=1,
        impact_score=2,
        mitigation_actions=[
            "Distribute ETL cron triggers across staggered 15-minute ingestion windows.",
            "Enable PgBouncer connection multiplexing on write nodes.",
        ],
        trend=RiskTrend.STABLE,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
    BusinessRiskItem(
        risk_id="risk-fin-005",
        pillar=RiskPillar.FINANCIAL_ANOMALY,
        title="EMEA Marketing Departmental Ledger Variance Spike",
        description="Q1 EMEA acquisition spending registered +14% above forecast due to unbudgeted regional summit sponsorships.",
        risk_score=10.0,
        priority_level=RiskPriority.LOW,
        financial_exposure_usd=24000.0,
        likelihood_score=2,
        impact_score=2,
        mitigation_actions=[
            "Enforce automated pre-approval threshold on marketing purchase orders exceeding $10k.",
            "Real-time ledger variance alerts via Part 1 automated email triggers.",
        ],
        trend=RiskTrend.STABLE,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
    BusinessRiskItem(
        risk_id="risk-sc-006",
        pillar=RiskPillar.SUPPLY_CHAIN_DISRUPTION,
        title="Single-Source ASIC Chipset Lead-Time Vulnerability",
        description="Primary semiconductor supplier indicates 28-day lead time on critical Fiber Switch ASICs.",
        risk_score=16.0,
        priority_level=RiskPriority.MEDIUM,
        financial_exposure_usd=110000.0,
        likelihood_score=3,
        impact_score=3,
        mitigation_actions=[
            "Qualify secondary semiconductor fabricator in Taiwan region.",
            "Maintain 45-day safety stock buffer calculated by Module 3 Inventory Optimizer.",
        ],
        trend=RiskTrend.STABLE,
        last_assessed_at="2026-08-31T06:00:00Z",
    ),
]


class BusinessRiskIntelligenceEngine:
    """Master Business Risk Intelligence Engine managing enterprise risk lifecycle."""

    _risks: Dict[str, BusinessRiskItem] = {r.risk_id: r for r in SEEDED_RISK_ITEMS}

    @classmethod
    def get_scorecard(cls) -> EnterpriseRiskScorecard:
        return CompositeRiskCalculator.calculate_scorecard(list(cls._risks.values()))

    @classmethod
    def list_risk_items(
        cls,
        pillar: Optional[RiskPillar] = None,
        priority: Optional[RiskPriority] = None,
    ) -> List[BusinessRiskItem]:
        items = list(cls._risks.values())
        if pillar:
            items = [i for i in items if i.pillar == pillar]
        if priority:
            items = [i for i in items if i.priority_level == priority]
        items.sort(key=lambda x: x.risk_score, reverse=True)
        return items

    @classmethod
    def evaluate_domain(
        cls,
        pillar: RiskPillar,
        parameters: Dict[str, Any],
    ) -> BusinessRiskItem:
        if pillar == RiskPillar.REVENUE_DECLINE:
            item = DomainRiskEvaluator.evaluate_revenue_decline(
                current_arr=parameters.get("current_arr", 24800000.0),
                yoy_growth_rate=parameters.get("yoy_growth_rate", 0.184),
            )
        elif pillar == RiskPillar.CUSTOMER_LOSS:
            item = DomainRiskEvaluator.evaluate_customer_loss(
                accounts_at_risk_arr=parameters.get("accounts_at_risk_arr", 480000.0),
                top_5_concentration_pct=parameters.get("top_5_concentration_pct", 28.0),
            )
        else:
            item = DomainRiskEvaluator.evaluate_supply_chain(
                max_lead_time_days=parameters.get("max_lead_time_days", 28),
            )

        cls._risks[item.risk_id] = item
        return item

    @classmethod
    def get_heatmap_data(cls) -> List[RiskHeatmapPoint]:
        points: List[RiskHeatmapPoint] = []
        for r in cls._risks.values():
            points.append(
                RiskHeatmapPoint(
                    risk_id=r.risk_id,
                    title=r.title,
                    pillar=r.pillar,
                    likelihood=r.likelihood_score,
                    impact=r.impact_score,
                    risk_score=r.risk_score,
                    priority=r.priority_level,
                )
            )
        return points
