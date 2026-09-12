from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.security_hardening.types import (
    RateLimitRule,
    SecurityHeaderCheck,
    SecurityPostureOverview,
    ThreatInspectionRequest,
    ThreatInspectionResult,
)


class SecurityHeaderCheckSchema(SecurityHeaderCheck):
    pass


class RateLimitRuleSchema(RateLimitRule):
    pass


class ThreatInspectionRequestSchema(ThreatInspectionRequest):
    pass


class ThreatInspectionResultSchema(ThreatInspectionResult):
    pass


class SecurityPostureOverviewSchema(SecurityPostureOverview):
    pass


class SecurityPostureResponse(BaseModel):
    posture: SecurityPostureOverviewSchema


class SecurityHeadersAuditResponse(BaseModel):
    total_headers: int
    headers: List[SecurityHeaderCheckSchema] = []


class ThreatInspectionResponse(BaseModel):
    inspection: ThreatInspectionResultSchema
