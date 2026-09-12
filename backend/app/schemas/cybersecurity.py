from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SecurityIncidentSummary(BaseModel):
    id: int
    incident_code: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # BRUTE_FORCE_ATTEMPT, ANOMALOUS_GEOLOCATION, PRIVILEGE_ESCALATION, EXCESSIVE_RATE_LIMIT, DATA_EXFILTRATION_SPIKE
    status: str  # OPEN, INVESTIGATING, MITIGATED, RESOLVED, FALSE_POSITIVE
    actor_ip: Optional[str] = None
    actor_email: Optional[str] = None
    location_country: Optional[str] = None
    event_count: int
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SecurityIncidentDetail(SecurityIncidentSummary):
    description: str
    mitigation_action_taken: Optional[str] = None


class IncidentActionRequest(BaseModel):
    action: str = Field(..., description="BLOCK_IP, TERMINATE_SESSION, RESOLVE, FALSE_POSITIVE")
    notes: Optional[str] = None


class IncidentActionResponse(BaseModel):
    incident_id: int
    incident_code: str
    status: str
    action_taken: str
    message: str


class ZeroTrustScorecardResponse(BaseModel):
    overall_risk_score: float
    risk_level: str  # OPTIMAL, ELEVATED, HIGH_RISK
    auth_entropy_score: float
    rbac_enclosure_score: float
    encryption_score: float
    anomaly_defense_score: float
    active_threats_count: int
    evaluated_at: datetime


class IPBlocklistResponse(BaseModel):
    id: int
    ip_address: str
    reason: str
    is_permanent: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CreateIPBlockRequest(BaseModel):
    ip_address: str = Field(..., min_length=7, max_length=50)
    reason: str = Field(..., min_length=3, max_length=255)
    is_permanent: bool = False
