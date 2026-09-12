from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ThreatVectorType(str, Enum):
    LOGIN_ANOMALY = "LOGIN_ANOMALY"
    BRUTE_FORCE = "BRUTE_FORCE"
    SUSPICIOUS_USER_ACTIVITY = "SUSPICIOUS_USER_ACTIVITY"
    FAILED_AUTH_ANALYSIS = "FAILED_AUTH_ANALYSIS"
    API_MISUSE = "API_MISUSE"
    DATA_ACCESS_ANOMALY = "DATA_ACCESS_ANOMALY"


class ThreatSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class IncidentStatus(str, Enum):
    ACTIVE_THREAT = "ACTIVE_THREAT"
    CONTAINED = "CONTAINED"
    QUARANTINED = "QUARANTINED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class SecurityActionType(str, Enum):
    EDGE_IP_QUARANTINE = "EDGE_IP_QUARANTINE"
    FORCE_MFA_RESET = "FORCE_MFA_RESET"
    REVOKE_USER_SESSION = "REVOKE_USER_SESSION"
    RATE_LIMIT_ENFORCEMENT = "RATE_LIMIT_ENFORCEMENT"
    AUDIT_LOG_ALERT = "AUDIT_LOG_ALERT"


class SecurityIncident(BaseModel):
    incident_id: str
    vector_type: ThreatVectorType
    title: str
    description: str
    severity: ThreatSeverity
    status: IncidentStatus
    source_ip: str
    target_user: Optional[str] = None
    mitre_tactic: str
    mitre_technique_id: str
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detected_at: str
    mitigated_at: Optional[str] = None
    recommended_playbook: SecurityActionType


class SecurityPostureSummary(BaseModel):
    zero_trust_score: float = Field(..., ge=0.0, le=100.0, description="0-25 Hardened, 26-50 Guarded, 51+ Vulnerable")
    posture_status: str
    active_threats_count: int
    quarantined_ips_count: int
    vector_distribution: Dict[str, int] = {}
    last_scan_timestamp: str


class MitreAttackMapping(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str
    associated_incidents_count: int
