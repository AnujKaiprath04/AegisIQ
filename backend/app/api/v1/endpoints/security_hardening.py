from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.security_hardening import (
    SecurityHeaderCheckSchema,
    SecurityHeadersAuditResponse,
    SecurityPostureOverviewSchema,
    SecurityPostureResponse,
    ThreatInspectionRequestSchema,
    ThreatInspectionResponse,
    ThreatInspectionResultSchema,
)
from app.security_hardening.engine import SecurityHardeningEngine

router = APIRouter(prefix="/security/hardening", tags=["Part 4 - Module 5: Security Hardening"])


@router.get("/posture", response_model=SecurityPostureResponse)
def get_security_posture(
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive platform security posture score (A+ Grade), active defense layers, and audit timestamps."""
    posture = SecurityHardeningEngine.get_posture()
    return SecurityPostureResponse(posture=SecurityPostureOverviewSchema(**posture.model_dump()))


@router.get("/headers", response_model=SecurityHeadersAuditResponse)
def get_security_headers_audit(
    current_user: User = Depends(get_current_user),
):
    """Audit active OWASP response security headers (HSTS, CSP, X-Frame-Options, Nosniff)."""
    headers = SecurityHardeningEngine.audit_headers()
    return SecurityHeadersAuditResponse(
        total_headers=len(headers),
        headers=[SecurityHeaderCheckSchema(**h.model_dump()) for h in headers],
    )


@router.post("/inspect", response_model=ThreatInspectionResponse)
def inspect_payload_threat(
    req: ThreatInspectionRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Scan and sanitize request payload for SQL Injection, XSS, Path Traversal, and Command Injection."""
    result = SecurityHardeningEngine.inspect_payload(req)
    return ThreatInspectionResponse(inspection=ThreatInspectionResultSchema(**result.model_dump()))
