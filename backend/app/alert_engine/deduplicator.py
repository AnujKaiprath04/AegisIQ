import hashlib
import time
from typing import Dict, Tuple


class AlertDeduplicationEngine:
    """Sliding-window hash fingerprint deduplication to prevent alert storms."""

    # key: md5_fingerprint -> value: last_triggered_epoch_seconds
    _seen_fingerprints: Dict[str, float] = {}

    @classmethod
    def generate_fingerprint(cls, rule_id: str, target_entity: str, severity: str) -> str:
        raw = f"{rule_id}:{target_entity}:{severity}".encode("utf-8")
        return hashlib.md5(raw).hexdigest()

    @classmethod
    def is_duplicate(cls, rule_id: str, target_entity: str, severity: str, window_minutes: int = 15) -> bool:
        fp = cls.generate_fingerprint(rule_id, target_entity, severity)
        now = time.time()
        last_seen = cls._seen_fingerprints.get(fp)

        if last_seen and (now - last_seen) < (window_minutes * 60):
            return True

        cls._seen_fingerprints[fp] = now
        return False
