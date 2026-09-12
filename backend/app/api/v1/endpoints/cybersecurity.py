from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.cybersecurity import (
    CreateIPBlockRequest,
    IPBlocklistResponse,
    IncidentActionRequest,
    IncidentActionResponse,
    SecurityIncidentDetail,
    SecurityIncidentSummary,
    ZeroTrustScorecardResponse,
)
from app.services.cybersecurity_service import CybersecurityService

router = APIRouter(prefix="/cybersecurity", tags=["Module 13: Cybersecurity Intelligence & SIEM"])


@router.get("/scorecard", response_model=ZeroTrustScorecardResponse)
def get_zero_trust_scorecard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve real-time zero-trust security posture risk score and defense vector breakdown."""
    return CybersecurityService.get_zero_trust_scorecard(db=db)


@router.get("/incidents", response_model=List[SecurityIncidentSummary])
def list_security_incidents(
    severity: Optional[str] = Query("ALL", description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW, ALL"),
    status_filter: Optional[str] = Query("ALL", description="Filter by status: OPEN, INVESTIGATING, MITIGATED, RESOLVED, FALSE_POSITIVE, ALL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List SIEM threat events, anomalous logins, and intrusion attempts."""
    return CybersecurityService.get_incidents(db=db, severity=severity, status_filter=status_filter)


@router.get("/incidents/{incident_id}", response_model=SecurityIncidentDetail)
def get_incident_detail(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full incident forensic telemetry and mitigation action records."""
    return CybersecurityService.get_incident_detail(db=db, incident_id=incident_id)


@router.post("/incidents/{incident_id}/action", response_model=IncidentActionResponse)
def take_remediation_action(
    incident_id: int,
    req: IncidentActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Trigger automated containment playbook: IP blocking, session revocation, or incident resolution."""
    return CybersecurityService.take_incident_action(db=db, incident_id=incident_id, req=req, user=current_user)


@router.get("/blocklist", response_model=List[IPBlocklistResponse])
def list_ip_blocklist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active firewall perimeter IP bans and quarantined addresses."""
    return CybersecurityService.get_blocklist(db=db)


@router.post("/blocklist", response_model=IPBlocklistResponse, status_code=status.HTTP_201_CREATED)
def add_ip_to_blocklist(
    req: CreateIPBlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Manually add an IP address to the perimeter security blocklist."""
    return CybersecurityService.add_to_blocklist(db=db, req=req, user=current_user)
