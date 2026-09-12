from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.recommendation_engine.types import (
    ImplementationEffort,
    RecommendationCard,
    RecommendationCategory,
    RecommendationCategorySummary,
    RecommendationPriority,
    RecommendationStatus,
    TimeHorizon,
)
from app.recommendation_engine.rules_engine import RuleBasedRecommender
from app.recommendation_engine.ml_recommender import MLPrescriptiveRecommender

SEEDED_RECOMMENDATIONS: List[RecommendationCard] = [
    RecommendationCard(
        recommendation_id="rec-ret-001",
        category=RecommendationCategory.CUSTOMER_RETENTION,
        title="Execute Executive Retention Playbook: Apex Global Logistics",
        description="High churn risk detected (74% churn probability). Secure $480k ARR contract through dedicated solutions engineering review.",
        priority=RecommendationPriority.CRITICAL,
        implementation_effort=ImplementationEffort.MEDIUM,
        time_horizon=TimeHorizon.IMMEDIATE_24H,
        expected_roi_usd=408000.0,
        confidence_score=0.94,
        rationale="Early sponsor alignment and resolution of adoption blockers restores account health before renewal deadline.",
        action_steps=[
            "Schedule VP-level alignment sync with primary stakeholder at Apex Global Logistics.",
            "Deploy dedicated Senior Solutions Architect to audit license utilization bottlenecks.",
            "Offer 15% renewal expansion credit on multi-year contract extension.",
        ],
        target_entity="ACC-APEX-001",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-prod-002",
        category=RecommendationCategory.PRODUCT_PROMOTION,
        title="Cross-Sell AI SIEM Threat Studio to Top 25 Enterprise Accounts",
        description="Collaborative filtering indicates 88% affinity for automated cybersecurity threat modules among accounts with >$100k ARR.",
        priority=RecommendationPriority.HIGH,
        implementation_effort=ImplementationEffort.MEDIUM,
        time_horizon=TimeHorizon.QUARTERLY_PLAN,
        expected_roi_usd=140000.0,
        confidence_score=0.91,
        rationale="High product affinity and existing SOC2 compliance mandates create strong organic upsell momentum.",
        action_steps=[
            "Deploy automated in-app feature discovery banner to Admin/CISO roles.",
            "Enable 14-day zero-trust sandbox trial with pre-populated telemetry demos.",
            "Equip Enterprise Account Executives with personalized ROI calculators.",
        ],
        target_entity="Enterprise Tier Accounts",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-inv-003",
        category=RecommendationCategory.INVENTORY_RESTOCKING,
        title="Emergency Purchase Order Release: Enterprise Fiber Switch 48-Port",
        description="Current stock (85 units) is below calculated Reorder Point (162 units). Release PO for 450 units to prevent Q4 stockouts.",
        priority=RecommendationPriority.HIGH,
        implementation_effort=ImplementationEffort.LOW,
        time_horizon=TimeHorizon.IMMEDIATE_24H,
        expected_roi_usd=38250.0,
        confidence_score=0.96,
        rationale="Prevents deferred fulfillment revenue losses and avoids expedited airfreight carrier surcharges.",
        action_steps=[
            "Issue Purchase Order for 450 units to primary supplier.",
            "Lock Q4 guaranteed shipment slot under existing master service agreement.",
        ],
        target_entity="SKU-OPT-100",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-cost-004",
        category=RecommendationCategory.COST_OPTIMIZATION,
        title="Prune 180 Inactive SaaS Licenses & Right-size AWS Aurora Database",
        description="Audit identified 180 dormant developer seats unused for >90 days and over-provisioned memory buffers on standby DB instances.",
        priority=RecommendationPriority.HIGH,
        implementation_effort=ImplementationEffort.LOW,
        time_horizon=TimeHorizon.NEXT_30_DAYS,
        expected_roi_usd=44800.0,
        confidence_score=0.98,
        rationale="Immediate reclamation of unused cloud subscriptions yields 100% margin savings with zero operational disruption.",
        action_steps=[
            "Deprovision 180 unused developer add-on seats via Okta SCIM sync.",
            "Downscale staging RDS Aurora replica from db.r6g.2xlarge to db.r6g.xlarge.",
            "Consolidate log retention policies to S3 Glacier storage tier.",
        ],
        target_entity="Cloud & SaaS Infrastructure",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-mkt-005",
        category=RecommendationCategory.MARKETING_CAMPAIGN,
        title="Launch Account-Based Marketing Campaign for EMEA FinTech Accounts",
        description="Predictive market basket analysis reveals 3.4x higher conversion rate for European financial technology prospects.",
        priority=RecommendationPriority.MEDIUM,
        implementation_effort=ImplementationEffort.MEDIUM,
        time_horizon=TimeHorizon.NEXT_30_DAYS,
        expected_roi_usd=95000.0,
        confidence_score=0.89,
        rationale="Targeting high-intent EMEA accounts drives +18% qualified pipeline with 22% lower customer acquisition cost (CAC).",
        action_steps=[
            "Build intent-driven LinkedIn Sponsored Content campaigns targeted at EMEA VP Engineering & Head of Data.",
            "Publish Banking & DORA Compliance Whitepaper highlighting AegisIQ explainability.",
        ],
        target_entity="EMEA FinTech Prospects",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-rev-006",
        category=RecommendationCategory.REVENUE_IMPROVEMENT,
        title="Upgrade High-Usage Commercial Accounts to Enterprise Tier",
        description="34 commercial accounts consistently consume >85% of monthly API quotas and request advanced SSO & RBAC support.",
        priority=RecommendationPriority.HIGH,
        implementation_effort=ImplementationEffort.LOW,
        time_horizon=TimeHorizon.NEXT_30_DAYS,
        expected_roi_usd=85000.0,
        confidence_score=0.92,
        rationale="Automated quota alerts incentivize proactive contract tier upgrades, expanding Net Revenue Retention (NRR) to 116%.",
        action_steps=[
            "Trigger automated in-app usage threshold notifications with 1-click upgrade proposals.",
            "Deploy Sales SDR outreach sequences to top 10 heavy API consumers.",
        ],
        target_entity="Commercial Account Cohort",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
    RecommendationCard(
        recommendation_id="rec-ops-007",
        category=RecommendationCategory.OPERATIONAL_WORKFLOW,
        title="Deploy Automated L1 Support Deflection via AegisIQ AI Assistant",
        description="Automate 42% of repetitive tier-1 support queries (password resets, API key rotation, invoice queries) using Part 2 Assistant.",
        priority=RecommendationPriority.MEDIUM,
        implementation_effort=ImplementationEffort.LOW,
        time_horizon=TimeHorizon.NEXT_30_DAYS,
        expected_roi_usd=32000.0,
        confidence_score=0.95,
        rationale="Reduces mean time to resolution (MTTR) by 64% and frees customer engineering bandwidth for enterprise accounts.",
        action_steps=[
            "Integrate Part 2 RAG assistant into customer support portal chat widget.",
            "Route verified authentication tokens directly into self-service API key management.",
        ],
        target_entity="Customer Support Portal",
        status=RecommendationStatus.ACTIVE,
        created_at="2026-08-31T06:00:00Z",
    ),
]


class EnterpriseRecommendationEngine:
    """Master Prescriptive Decision & Recommendation Engine for AegisIQ."""

    _catalog: Dict[str, RecommendationCard] = {r.recommendation_id: r for r in SEEDED_RECOMMENDATIONS}

    @classmethod
    def list_recommendations(
        cls,
        category: Optional[RecommendationCategory] = None,
        priority: Optional[RecommendationPriority] = None,
        status_filter: Optional[RecommendationStatus] = None,
    ) -> List[RecommendationCard]:
        cards = list(cls._catalog.values())

        if category:
            cards = [c for c in cards if c.category == category]
        if priority:
            cards = [c for c in cards if c.priority == priority]
        if status_filter:
            cards = [c for c in cards if c.status == status_filter]

        # Sort by expected ROI descending
        cards.sort(key=lambda x: x.expected_roi_usd, reverse=True)
        return cards

    @classmethod
    def generate_recommendations(
        cls,
        target_type: str,
        target_id: str,
        parameters: Dict[str, Any],
    ) -> List[RecommendationCard]:
        generated: List[RecommendationCard] = []

        if target_type == "ACCOUNT":
            prob = parameters.get("churn_probability", 0.74)
            arr = parameters.get("arr_usd", 480000.0)
            name = parameters.get("company_name", "Apex Global Logistics")
            card = RuleBasedRecommender.evaluate_churn_risk(target_id, name, prob, arr)
            if card:
                cls._catalog[card.recommendation_id] = card
                generated.append(card)

        elif target_type == "INVENTORY":
            curr = parameters.get("current_stock", 50)
            rop = parameters.get("reorder_point", 150)
            price = parameters.get("unit_price_usd", 120.0)
            p_name = parameters.get("product_name", "Enterprise Cloud Blade")
            card = RuleBasedRecommender.evaluate_inventory_stockout(target_id, p_name, curr, rop, price)
            if card:
                cls._catalog[card.recommendation_id] = card
                generated.append(card)

        else:
            cost_card = MLPrescriptiveRecommender.generate_cost_optimization()
            cls._catalog[cost_card.recommendation_id] = cost_card
            generated.append(cost_card)

        return generated

    @classmethod
    def apply_recommendation(cls, recommendation_id: str) -> RecommendationCard:
        card = cls._catalog.get(recommendation_id)
        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recommendation '{recommendation_id}' not found.")

        card.status = RecommendationStatus.APPLIED
        card.applied_at = datetime.now(timezone.utc).isoformat()
        return card

    @classmethod
    def get_category_summary(cls) -> List[RecommendationCategorySummary]:
        summaries: List[RecommendationCategorySummary] = []
        for cat in RecommendationCategory:
            cards = [c for c in cls._catalog.values() if c.category == cat]
            active = len([c for c in cards if c.status == RecommendationStatus.ACTIVE])
            applied = len([c for c in cards if c.status == RecommendationStatus.APPLIED])
            roi_sum = sum(c.expected_roi_usd for c in cards)
            summaries.append(
                RecommendationCategorySummary(
                    category=cat,
                    active_count=active,
                    applied_count=applied,
                    total_potential_roi_usd=round(roi_sum, 2),
                )
            )
        return summaries
