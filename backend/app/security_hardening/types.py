from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ThreatCategory(str, Enum):
    SQL_INJECTION = "SQL_INJECTION"
    CROSS_SITE_SCRIPTING = "CROSS_SITE_SCRIPTING"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    BENIGN = "BENIGN"


class SecurityHeaderCheck(BaseModel):
    header_name: str
    configured_value: str
    standard: str
    status: str = "COMPLIANT"


class RateLimitRule(BaseModel):
    client_tier: str
    max_requests_per_minute: int
    burst_capacity: int
    sliding_window_seconds: int = 60


class ThreatInspectionRequest(BaseModel):
    payload: str = Field(..., description="String payload to inspect for security threats")
    context: str = Field(default="api_request_body", description="Context of inspection")


class ThreatInspectionResult(BaseModel):
    is_threat_detected: bool
    detected_category: ThreatCategory
    matched_pattern: Optional[str] = None
    sanitized_output: str
    risk_level: str
    inspection_timestamp: str


class SecurityPostureOverview(BaseModel):
    posture_score: float = Field(default=98.5, ge=0.0, le=100.0)
    compliance_grade: str = "A+ (Enterprise Hardened)"
    owasp_top_10_compliant: bool = True
    active_defense_layers: List[str] = []
    header_checks: List[SecurityHeaderCheck] = []
    rate_limit_rules: List[RateLimitRule] = []
    last_audit_timestamp: str
