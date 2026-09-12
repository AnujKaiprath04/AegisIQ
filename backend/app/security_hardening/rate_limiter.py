import time
from typing import Dict, List, Tuple
from app.security_hardening.types import RateLimitRule

RATE_LIMIT_RULES: List[RateLimitRule] = [
    RateLimitRule(client_tier="SUPER_ADMIN", max_requests_per_minute=300, burst_capacity=50),
    RateLimitRule(client_tier="ADMIN", max_requests_per_minute=180, burst_capacity=30),
    RateLimitRule(client_tier="STANDARD_USER", max_requests_per_minute=120, burst_capacity=20),
    RateLimitRule(client_tier="UNAUTHENTICATED", max_requests_per_minute=30, burst_capacity=5),
    RateLimitRule(client_tier="AUTH_ENDPOINT", max_requests_per_minute=10, burst_capacity=2),
]


class EnterpriseTokenBucketRateLimiter:
    """Sliding-window token bucket rate limiter with multi-tier quotas."""

    _buckets: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_update)

    @classmethod
    def get_rules(cls) -> List[RateLimitRule]:
        return RATE_LIMIT_RULES

    @classmethod
    def check_rate_limit(cls, key: str, tier: str = "STANDARD_USER") -> Tuple[bool, int, int, int]:
        rule = next((r for r in RATE_LIMIT_RULES if r.client_tier == tier), RATE_LIMIT_RULES[2])
        capacity = float(rule.max_requests_per_minute)
        refill_rate = capacity / 60.0  # tokens per second

        now = time.time()
        if key not in cls._buckets:
            cls._buckets[key] = (capacity - 1.0, now)
            return True, int(capacity - 1), int(capacity), 60

        tokens, last_update = cls._buckets[key]
        elapsed = now - last_update
        tokens = min(capacity, tokens + elapsed * refill_rate)

        if tokens >= 1.0:
            tokens -= 1.0
            cls._buckets[key] = (tokens, now)
            return True, int(tokens), int(capacity), int(60 - (elapsed % 60))
        else:
            cls._buckets[key] = (tokens, now)
            return False, 0, int(capacity), int(60 - (elapsed % 60))
