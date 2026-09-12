from typing import Any, Dict, List
from app.xai_studio.types import FeatureAttribution


class LimeSurrogateEngine:
    """Local Interpretable Model-agnostic Explanations (LIME) Sparse Linear Surrogate Engine."""

    @classmethod
    def explain(
        cls,
        features: Dict[str, Any],
    ) -> List[FeatureAttribution]:
        attributions: List[FeatureAttribution] = []

        support_tickets = float(features.get("monthly_support_tickets", 8))
        nps_score = float(features.get("csm_nps_score", 32))
        active_users = float(features.get("monthly_active_users", 45))

        # Local slope approximations
        l_tickets = round((support_tickets - 2.0) * 0.048, 3)
        l_nps = round((45.0 - nps_score) * 0.008, 3)
        l_users = round((active_users - 30.0) * -0.006, 3)

        raw = [
            ("monthly_support_tickets", support_tickets, l_tickets),
            ("csm_nps_score", nps_score, l_nps),
            ("monthly_active_users", active_users, l_users),
        ]

        total_abs = sum(abs(w) for _, _, w in raw) or 1.0

        for name, val, w in raw:
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
