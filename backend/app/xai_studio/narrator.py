from typing import List
from app.xai_studio.types import FeatureAttribution


class XAINarrativeSynthesizer:
    """Synthesizes human-readable, executive-ready governance narratives from SHAP and LIME weights."""

    @classmethod
    def synthesize(
        cls,
        model_name: str,
        probability: float,
        shap_values: List[FeatureAttribution],
    ) -> str:
        top_risk_drivers = [s for s in shap_values if s.impact_direction == "POSITIVE_RISK"][:2]
        top_mitigators = [s for s in shap_values if s.impact_direction == "NEGATIVE_RISK"][:1]

        risk_str = ", ".join(f"{d.feature_name} (attribution: +{d.attribution_weight:.2f})" for d in top_risk_drivers)
        mit_str = ", ".join(f"{m.feature_name} (attribution: {m.attribution_weight:.2f})" for m in top_mitigators)

        narrative = (
            f"The {model_name} model evaluated this instance with a {int(probability * 100)}% risk probability. "
            f"The primary risk escalators are {risk_str}. "
        )
        if mit_str:
            narrative += f"Conversely, healthy indicators such as {mit_str} partially mitigated downside risk."

        return narrative
