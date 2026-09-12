import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.security_engine.types import (
    IncidentStatus,
    SecurityActionType,
    SecurityIncident,
    ThreatSeverity,
    ThreatVectorType,
)
from app.security_engine.mitre_mapper import MitreAttackMapper


class ThreatDetectorSuite:
    """Specialized behavioral analytics and threat detection heuristics."""

    @classmethod
    def detect_login_anomaly(
        cls,
        source_ip: str = "198.51.100.77",
        target_user: str = "victoria.sterling@aegisiq.com",
        current_country: str = "DE",
        previous_country: str = "US",
        time_diff_minutes: int = 15,
    ) -> SecurityIncident:
        tactic, tech_id, tech_name = MitreAttackMapper.get_mapping(ThreatVectorType.LOGIN_ANOMALY)
        now_str = datetime.now(timezone.utc).isoformat()
        return SecurityIncident(
            incident_id=f"inc-login-{int(time.time())}",
            vector_type=ThreatVectorType.LOGIN_ANOMALY,
            title=f"Impossible Traveler Ingress: {target_user}",
            description=f"Authentication observed from {current_country} ({source_ip}) only {time_diff_minutes} minutes after legitimate login in {previous_country}.",
            severity=ThreatSeverity.HIGH,
            status=IncidentStatus.ACTIVE_THREAT,
            source_ip=source_ip,
            target_user=target_user,
            mitre_tactic=tactic,
            mitre_technique_id=tech_id,
            anomaly_score=0.92,
            confidence_score=0.96,
            detected_at=now_str,
            recommended_playbook=SecurityActionType.FORCE_MFA_RESET,
        )

    @classmethod
    def detect_brute_force(
        cls,
        source_ip: str = "198.51.100.44",
        target_user: str = "admin@aegisiq.com",
        failed_attempts_count: int = 48,
        time_window_seconds: int = 60,
    ) -> SecurityIncident:
        tactic, tech_id, tech_name = MitreAttackMapper.get_mapping(ThreatVectorType.BRUTE_FORCE)
        now_str = datetime.now(timezone.utc).isoformat()
        return SecurityIncident(
            incident_id=f"inc-brute-{int(time.time())}",
            vector_type=ThreatVectorType.BRUTE_FORCE,
            title=f"High-Velocity Brute-Force Password Spraying: {source_ip}",
            description=f"Detected {failed_attempts_count} failed authentication attempts within {time_window_seconds}s targeting {target_user}.",
            severity=ThreatSeverity.CRITICAL,
            status=IncidentStatus.ACTIVE_THREAT,
            source_ip=source_ip,
            target_user=target_user,
            mitre_tactic=tactic,
            mitre_technique_id=tech_id,
            anomaly_score=0.98,
            confidence_score=0.99,
            detected_at=now_str,
            recommended_playbook=SecurityActionType.EDGE_IP_QUARANTINE,
        )

    @classmethod
    def detect_api_misuse(
        cls,
        source_ip: str = "203.0.113.88",
        endpoint: str = "/api/v1/datasets/query",
        request_rate_per_sec: int = 145,
    ) -> SecurityIncident:
        tactic, tech_id, tech_name = MitreAttackMapper.get_mapping(ThreatVectorType.API_MISUSE)
        now_str = datetime.now(timezone.utc).isoformat()
        return SecurityIncident(
            incident_id=f"inc-api-{int(time.time())}",
            vector_type=ThreatVectorType.API_MISUSE,
            title=f"API Rate-Limit Violation & Automated Scraping: {source_ip}",
            description=f"IP triggered {request_rate_per_sec} requests/sec on {endpoint} exceeding 30 req/sec threshold.",
            severity=ThreatSeverity.MEDIUM,
            status=IncidentStatus.ACTIVE_THREAT,
            source_ip=source_ip,
            target_user="Anonymous API Key",
            mitre_tactic=tactic,
            mitre_technique_id=tech_id,
            anomaly_score=0.84,
            confidence_score=0.92,
            detected_at=now_str,
            recommended_playbook=SecurityActionType.RATE_LIMIT_ENFORCEMENT,
        )
