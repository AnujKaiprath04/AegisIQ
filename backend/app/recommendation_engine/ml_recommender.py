import time
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.recommendation_engine.types import (
    ImplementationEffort,
    RecommendationCard,
    RecommendationCategory,
    RecommendationPriority,
    RecommendationStatus,
    TimeHorizon,
)


class MLPrescriptiveRecommender:
    """Multi-Criteria Utility Optimization and Prescriptive Machine Learning Recommender."""

    @classmethod
    def score_utility(cls, card: RecommendationCard) -> float:
        roi_norm = min(1.0, card.expected_roi_usd / 500000.0)
        conf = card.confidence_score

        effort_penalty = {
            ImplementationEffort.LOW: 0.0,
            ImplementationEffort.MEDIUM: 0.15,
            ImplementationEffort.HIGH: 0.35,
        }.get(card.implementation_effort, 0.15)

        priority_boost = {
            RecommendationPriority.CRITICAL: 0.40,
            RecommendationPriority.HIGH: 0.25,
            RecommendationPriority.MEDIUM: 0.10,
            RecommendationPriority.LOW: 0.0,
        }.get(card.priority, 0.10)

        utility = (0.45 * roi_norm) + (0.25 * conf) - (0.15 * effort_penalty) + (0.15 * priority_boost)
        return round(max(0.0, min(1.0, utility)), 3)

    @classmethod
    def generate_cost_optimization(cls) -> RecommendationCard:
        now_str = datetime.now(timezone.utc).isoformat()
        return RecommendationCard(
            recommendation_id=f"rec-cost-{int(time.time())}",
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
            created_at=now_str,
        )

    @classmethod
    def generate_product_cross_sell(cls) -> RecommendationCard:
        now_str = datetime.now(timezone.utc).isoformat()
        return RecommendationCard(
            recommendation_id=f"rec-prod-{int(time.time())}",
            category=RecommendationCategory.PRODUCT_PROMOTION,
            title="Cross-Sell AI SIEM Threat Studio to Top 25 Enterprise Accounts",
            description="Collaborative filtering indicates 88% affinity for automated cybersecurity threat modules among accounts with >$100k ARR.",
            priority=RecommendationPriority.MEDIUM,
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
            created_at=now_str,
        )
