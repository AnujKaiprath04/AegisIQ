from typing import Tuple


class EscalationPolicyManager:
    """Multi-Tier time-delayed escalation ladder."""

    @classmethod
    def get_tier_for_elapsed(cls, elapsed_minutes: float) -> Tuple[int, str]:
        if elapsed_minutes >= 60.0:
            return 3, "Tier 3: VP & C-Level Executive Notification"
        elif elapsed_minutes >= 15.0:
            return 2, "Tier 2: Engineering / Account Lead Escalation"
        else:
            return 1, "Tier 1: On-Call Analyst / CSM Initial Response"
