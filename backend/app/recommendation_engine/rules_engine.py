import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.recommendation_engine.types import (
    ImplementationEffort,
    RecommendationCard,
    RecommendationCategory,
    RecommendationPriority,
    RecommendationStatus,
    TimeHorizon,
)


class RuleBasedRecommender:
    """Heuristic and policy-driven rule evaluation engine for immediate operational action triggers."""

    @classmethod
    def evaluate_churn_risk(
        cls,
        account_id: str,
        company_name: str,
        churn_probability: float,
        arr_usd: float,
    ) -> Optional[RecommendationCard]:
        if churn_probability >= 0.65:
            rec_id = f"rec-retention-{int(time.time())}"
            now_str = datetime.now(timezone.utc).isoformat()
            return RecommendationCard(
                recommendation_id=rec_id,
                category=RecommendationCategory.CUSTOMER_RETENTION,
                title=f"Execute Executive Retention Playbook: {company_name}",
                description=f"{company_name} is in critical churn danger ({int(churn_probability * 100)}% probability) threatening ${int(arr_usd):,} ARR.",
                priority=RecommendationPriority.CRITICAL,
                implementation_effort=ImplementationEffort.MEDIUM,
                time_horizon=TimeHorizon.IMMEDIATE_24H,
                expected_roi_usd=round(arr_usd * 0.85, 2),
                confidence_score=0.94,
                rationale="Prompt multi-threaded executive engagement prevents contract cancellation and restores healthy NPS adoption.",
                action_steps=[
                    f"Schedule VP-level alignment sync with primary stakeholder at {company_name}.",
                    "Deploy dedicated Senior Solutions Architect to audit license utilization bottlenecks.",
                    "Offer 15% renewal expansion credit on multi-year contract extension.",
                ],
                target_entity=account_id,
                status=RecommendationStatus.ACTIVE,
                created_at=now_str,
            )
        return None

    @classmethod
    def evaluate_inventory_stockout(
        cls,
        sku_id: str,
        product_name: str,
        current_stock: int,
        reorder_point: int,
        unit_price_usd: float,
    ) -> Optional[RecommendationCard]:
        if current_stock <= reorder_point:
            rec_id = f"rec-inv-{int(time.time())}"
            now_str = datetime.now(timezone.utc).isoformat()
            deficit = reorder_point - current_stock
            risk_loss = (deficit + 100) * unit_price_usd
            return RecommendationCard(
                recommendation_id=rec_id,
                category=RecommendationCategory.INVENTORY_RESTOCKING,
                title=f"Emergency Purchase Order Release: {product_name}",
                description=f"Current inventory level ({current_stock} units) has breached safety threshold (ROP: {reorder_point} units).",
                priority=RecommendationPriority.HIGH,
                implementation_effort=ImplementationEffort.LOW,
                time_horizon=TimeHorizon.IMMEDIATE_24H,
                expected_roi_usd=round(risk_loss, 2),
                confidence_score=0.96,
                rationale="Stockout risk during peak quarter will trigger customer SLA penalties and delivery deferrals.",
                action_steps=[
                    f"Issue Purchase Order for {deficit + 250} units to Tier-1 primary supplier.",
                    "Request expedited air freight option to compress transit window to 5 business days.",
                    "Notify sales operations to adjust backorder delivery ETA commitments.",
                ],
                target_entity=sku_id,
                status=RecommendationStatus.ACTIVE,
                created_at=now_str,
            )
        return None
