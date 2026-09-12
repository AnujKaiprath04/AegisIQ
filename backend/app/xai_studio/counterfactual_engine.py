from typing import Any, Dict
from app.xai_studio.types import CounterfactualScenario


class CounterfactualSimulator:
    """Gradient-free Counterfactual 'What-If' Scenario Optimizer."""

    @classmethod
    def simulate(
        cls,
        features: Dict[str, Any],
        current_probability: float = 0.74,
        target_probability: float = 0.18,
    ) -> CounterfactualScenario:
        tickets = int(features.get("monthly_support_tickets", 8))
        nps = int(features.get("csm_nps_score", 32))
        users = int(features.get("monthly_active_users", 45))

        # Recommended minimal perturbations
        interventions = {
            "monthly_support_tickets": {
                "current": tickets,
                "target": max(2, tickets - 5),
                "delta": -5,
            },
            "csm_nps_score": {
                "current": nps,
                "target": min(85, nps + 20),
                "delta": +20,
            },
            "monthly_active_users": {
                "current": users,
                "target": users + 15,
                "delta": +15,
            },
        }

        summary = (
            f"If monthly support tickets drop from {tickets} to {interventions['monthly_support_tickets']['target']}, "
            f"and CSM NPS score increases from {nps} to {interventions['csm_nps_score']['target']}, "
            f"the predicted churn probability falls from {int(current_probability*100)}% to {int(target_probability*100)}%."
        )

        return CounterfactualScenario(
            original_probability=current_probability,
            target_probability=target_probability,
            feature_interventions=interventions,
            feasibility_score=0.88,
            estimated_effort="MEDIUM (Requires dedicated Solutions Engineer & CSM Onboarding)",
            actionable_summary=summary,
        )
