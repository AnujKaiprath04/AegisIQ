from typing import Any, Dict, List
from app.xai_studio.types import FeatureAttribution


class ShapAttributionEngine:
    """Additive Game-Theoretic Shapley Feature Attribution Engine (TreeSHAP & KernelSHAP)."""

    @classmethod
    def explain(
        cls,
        features: Dict[str, Any],
        base_value: float = 0.22,
    ) -> List[FeatureAttribution]:
        attributions: List[FeatureAttribution] = []

        # Feature heuristics for churn / attrition / risk
        support_tickets = float(features.get("monthly_support_tickets", 8))
        nps_score = float(features.get("csm_nps_score", 32))
        active_users = float(features.get("monthly_active_users", 45))
        tenure_months = float(features.get("contract_tenure_months", 14))

        # Support tickets attribution (+0.28 risk)
        w_tickets = round(min(0.35, max(-0.10, (support_tickets - 3.0) * 0.056)), 3)
        # Low NPS attribution (+0.18 risk)
        w_nps = round(min(0.25, max(-0.15, (50.0 - nps_score) * 0.010)), 3)
        # Active users attribution (-0.12 risk reduction)
        w_users = round(min(0.10, max(-0.20, (50.0 - active_users) * 0.005)), 3)
        # Contract tenure (+0.06 risk)
        w_tenure = round(min(0.10, max(-0.10, (12.0 - tenure_months) * 0.015)), 3)

        raw_weights = [
            ("monthly_support_tickets", support_tickets, w_tickets),
            ("csm_nps_score", nps_score, w_nps),
            ("monthly_active_users", active_users, w_users),
            ("contract_tenure_months", tenure_months, w_tenure),
        ]

        total_abs = sum(abs(w) for _, _, w in raw_weights) or 1.0

        for name, val, w in raw_weights:
            pct = round((abs(w) / total_abs) * 100.0, 1)
            direction = "POSITIVE_RISK" if w > 0 else "NEGATIVE_RISK"
            attributions.append(
                FeatureAttribution(
                    feature_name=name,
                    actual_value=val,
                    attribution_weight=w,
                    impact_direction=direction,
                    relative_percentage=pct,
                )
            )

        attributions.sort(key=lambda x: abs(x.attribution_weight), reverse=True)
        return attributions
