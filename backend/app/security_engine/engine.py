from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.security_engine.types import (
    IncidentStatus,
    MitreAttackMapping,
    SecurityActionType,
    SecurityIncident,
    SecurityPostureSummary,
    ThreatSeverity,
    ThreatVectorType,
)
from app.security_engine.detectors import ThreatDetectorSuite
from app.security_engine.mitre_mapper import MitreAttackMapper, MITRE_TECHNIQUE_CATALOG

SEEDED_SECURITY_INCIDENTS: List[SecurityIncident] = [
    SecurityIncident(
        incident_id="inc-sec-001",
        vector_type=ThreatVectorType.BRUTE_FORCE,
        title="High-Velocity Brute-Force Password Spraying",
        description="Detected 48 failed authentication attempts within 60s targeting admin@aegisiq.com from 198.51.100.44.",
        severity=ThreatSeverity.CRITICAL,
        status=IncidentStatus.QUARANTINED,
        source_ip="198.51.100.44",
        target_user="admin@aegisiq.com",
        mitre_tactic="Credential Access",
        mitre_technique_id="T1110.001",
        anomaly_score=0.98,
        confidence_score=0.99,
        detected_at="2026-08-31T06:00:00Z",
        mitigated_at="2026-08-31T06:01:12Z",
        recommended_playbook=SecurityActionType.EDGE_IP_QUARANTINE,
    ),
    SecurityIncident(
        incident_id="inc-sec-002",
        vector_type=ThreatVectorType.LOGIN_ANOMALY,
        title="Impossible Traveler Ingress: Victoria Sterling",
        description="Authentication observed from Frankfurt, Germany (198.51.100.77) only 15 minutes after legitimate login in New York, USA.",
        severity=ThreatSeverity.HIGH,
        status=IncidentStatus.CONTAINED,
        source_ip="198.51.100.77",
        target_user="victoria.sterling@aegisiq.com",
        mitre_tactic="Initial Access",
        mitre_technique_id="T1078.004",
        anomaly_score=0.92,
        confidence_score=0.96,
        detected_at="2026-08-31T06:15:00Z",
        mitigated_at="2026-08-31T06:16:30Z",
        recommended_playbook=SecurityActionType.FORCE_MFA_RESET,
    ),
    SecurityIncident(
        incident_id="inc-sec-003",
        vector_type=ThreatVectorType.SUSPICIOUS_USER_ACTIVITY,
        title="Unscheduled Superuser Policy Elevation",
        description="Service account svc-etl-batch requested administrative IAM role alteration outside scheduled maintenance window.",
        severity=ThreatSeverity.MEDIUM,
        status=IncidentStatus.ACTIVE_THREAT,
        source_ip="10.0.4.12",
        target_user="svc-etl-batch",
        mitre_tactic="Privilege Escalation",
        mitre_technique_id="T1078",
        anomaly_score=0.86,
        confidence_score=0.91,
        detected_at="2026-08-31T06:30:00Z",
        recommended_playbook=SecurityActionType.AUDIT_LOG_ALERT,
    ),
    SecurityIncident(
        incident_id="inc-sec-004",
        vector_type=ThreatVectorType.FAILED_AUTH_ANALYSIS,
        title="Expired JWT Token Signature Replay Attempt",
        description="Attempted invocation of /api/v1/reports with signed token expired >72 hours ago from legacy user-agent.",
        severity=ThreatSeverity.LOW,
        status=IncidentStatus.RESOLVED,
        source_ip="198.51.100.12",
        target_user="former.employee@aegisiq.com",
        mitre_tactic="Defense Evasion",
        mitre_technique_id="T1556",
        anomaly_score=0.68,
        confidence_score=0.94,
        detected_at="2026-08-31T06:45:00Z",
        mitigated_at="2026-08-31T06:46:00Z",
        recommended_playbook=SecurityActionType.REVOKE_USER_SESSION,
    ),
    SecurityIncident(
        incident_id="inc-sec-005",
        vector_type=ThreatVectorType.API_MISUSE,
        title="Automated Rate-Limit Violation on Telemetry Ingress",
        description="IP 203.0.113.88 executed 145 req/sec querying dataset metadata endpoints, triggering edge rate-limiting throttle.",
        severity=ThreatSeverity.MEDIUM,
        status=IncidentStatus.CONTAINED,
        source_ip="203.0.113.88",
        target_user="Anonymous API Key",
        mitre_tactic="Discovery",
        mitre_technique_id="T1059",
        anomaly_score=0.84,
        confidence_score=0.92,
        detected_at="2026-08-31T07:00:00Z",
        mitigated_at="2026-08-31T07:01:00Z",
        recommended_playbook=SecurityActionType.RATE_LIMIT_ENFORCEMENT,
    ),
    SecurityIncident(
        incident_id="inc-sec-006",
        vector_type=ThreatVectorType.DATA_ACCESS_ANOMALY,
        title="Off-Hours Bulk Financial Dataset Export",
        description="User downloaded 450,000 records from financial ledger at 02:14 AM UTC without prior batch export ticket.",
        severity=ThreatSeverity.HIGH,
        status=IncidentStatus.CONTAINED,
        source_ip="10.2.14.8",
        target_user="external.contractor@aegisiq.com",
        mitre_tactic="Exfiltration",
        mitre_technique_id="T1020",
        anomaly_score=0.89,
        confidence_score=0.95,
        detected_at="2026-08-31T07:15:00Z",
        mitigated_at="2026-08-31T07:18:00Z",
        recommended_playbook=SecurityActionType.AUDIT_LOG_ALERT,
    ),
]


class EnterpriseSecurityEngine:
    """Master Cybersecurity Intelligence & SIEM Threat Analytics Engine."""

    _incidents: Dict[str, SecurityIncident] = {i.incident_id: i for i in SEEDED_SECURITY_INCIDENTS}

    @classmethod
    def get_posture(cls) -> SecurityPostureSummary:
        now_str = datetime.now(timezone.utc).isoformat()
        active = [i for i in cls._incidents.values() if i.status == IncidentStatus.ACTIVE_THREAT]
        quarantined = [i for i in cls._incidents.values() if i.status == IncidentStatus.QUARANTINED]

        dist: Dict[str, int] = {}
        for i in cls._incidents.values():
            dist[i.vector_type.value] = dist.get(i.vector_type.value, 0) + 1

        # Zero-Trust Score: 12.0 / 100 (Hardened)
        return SecurityPostureSummary(
            zero_trust_score=12.0,
            posture_status="HARDENED_ZERO_TRUST_POSTURE",
            active_threats_count=len(active),
            quarantined_ips_count=max(1, len(quarantined)),
            vector_distribution=dist,
            last_scan_timestamp=now_str,
        )

    @classmethod
    def list_incidents(
        cls,
        vector: Optional[ThreatVectorType] = None,
        severity: Optional[ThreatSeverity] = None,
        status_filter: Optional[IncidentStatus] = None,
    ) -> List[SecurityIncident]:
        incidents = list(cls._incidents.values())
        if vector:
            incidents = [i for i in incidents if i.vector_type == vector]
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if status_filter:
            incidents = [i for i in incidents if i.status == status_filter]

        incidents.sort(key=lambda x: x.anomaly_score, reverse=True)
        return incidents

    @classmethod
    def analyze_event(
        cls,
        event_type: ThreatVectorType,
        payload: Dict[str, Any],
    ) -> SecurityIncident:
        if event_type == ThreatVectorType.LOGIN_ANOMALY:
            inc = ThreatDetectorSuite.detect_login_anomaly(
                source_ip=payload.get("source_ip", "198.51.100.77"),
                target_user=payload.get("target_user", "victoria.sterling@aegisiq.com"),
                current_country=payload.get("current_country", "DE"),
                previous_country=payload.get("previous_country", "US"),
            )
        elif event_type == ThreatVectorType.BRUTE_FORCE:
            inc = ThreatDetectorSuite.detect_brute_force(
                source_ip=payload.get("source_ip", "198.51.100.44"),
                target_user=payload.get("target_user", "admin@aegisiq.com"),
                failed_attempts_count=payload.get("failed_attempts_count", 48),
            )
        else:
            inc = ThreatDetectorSuite.detect_api_misuse(
                source_ip=payload.get("source_ip", "203.0.113.88"),
                endpoint=payload.get("endpoint", "/api/v1/datasets/query"),
                request_rate_per_sec=payload.get("request_rate_per_sec", 145),
            )

        cls._incidents[inc.incident_id] = inc
        return inc

    @classmethod
    def execute_mitigation(
        cls,
        incident_id: str,
        action_type: SecurityActionType,
    ) -> SecurityIncident:
        inc = cls._incidents.get(incident_id)
        if not inc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")

        if action_type == SecurityActionType.EDGE_IP_QUARANTINE:
            inc.status = IncidentStatus.QUARANTINED
        else:
            inc.status = IncidentStatus.CONTAINED

        inc.mitigated_at = datetime.now(timezone.utc).isoformat()
        return inc

    @classmethod
    def get_mitre_matrix(cls) -> List[MitreAttackMapping]:
        mappings: List[MitreAttackMapping] = []
        for vec, (tactic, tech_id, name) in MITRE_TECHNIQUE_CATALOG.items():
            count = len([i for i in cls._incidents.values() if i.vector_type == vec])
            mappings.append(
                MitreAttackMapping(
                    tactic=tactic,
                    technique_id=tech_id,
                    technique_name=name,
                    associated_incidents_count=count,
                )
            )
        return mappings
