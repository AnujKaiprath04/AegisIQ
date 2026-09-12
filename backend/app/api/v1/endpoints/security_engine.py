from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.security_engine import (
    MitigationExecutionRequest,
    MitigationExecutionResponse,
    MitreAttackMappingSchema,
    MitreMatrixResponse,
    SecurityIncidentListResponse,
    SecurityIncidentSchema,
    SecurityPostureSummarySchema,
    ThreatEventAnalysisRequest,
)
from app.security_engine.engine import EnterpriseSecurityEngine
from app.security_engine.types import (
    IncidentStatus,
    ThreatSeverity,
    ThreatVectorType,
)

router = APIRouter(prefix="/ml/security", tags=["Part 3 - Module 6: Cybersecurity Intelligence"])


@router.get("/posture", response_model=SecurityPostureSummarySchema)
def get_security_posture(
    current_user: User = Depends(get_current_user),
):
    """Retrieve global Zero-Trust security posture scorecard and active threat summary."""
    posture = EnterpriseSecurityEngine.get_posture()
    return SecurityPostureSummarySchema(**posture.model_dump())


@router.get("/incidents", response_model=SecurityIncidentListResponse)
def list_security_incidents(
    vector: Optional[ThreatVectorType] = Query(None, description="Filter by threat vector"),
    severity: Optional[ThreatSeverity] = Query(None, description="Filter by severity level"),
    status: Optional[IncidentStatus] = Query(None, description="Filter by incident status"),
    current_user: User = Depends(get_current_user),
):
    """List detected security incidents sorted by anomaly score descending."""
    incidents = EnterpriseSecurityEngine.list_incidents(
        vector=vector,
        severity=severity,
        status_filter=status,
    )
    return SecurityIncidentListResponse(
        total_incidents=len(incidents),
        incidents=[SecurityIncidentSchema(**i.model_dump()) for i in incidents],
    )


@router.post("/analyze-event", response_model=SecurityIncidentSchema)
def analyze_telemetry_event(
    req: ThreatEventAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Ingest raw access/auth telemetry and run real-time behavioral ML threat detection."""
    incident = EnterpriseSecurityEngine.analyze_event(
        event_type=req.event_type,
        payload=req.payload,
    )
    return SecurityIncidentSchema(**incident.model_dump())


@router.post("/incidents/{incident_id}/mitigate", response_model=MitigationExecutionResponse)
def execute_incident_mitigation(
    incident_id: str,
    req: MitigationExecutionRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute automated or manual containment playbook (e.g. Edge IP Quarantine, Session Revocation)."""
    incident = EnterpriseSecurityEngine.execute_mitigation(
        incident_id=incident_id,
        action_type=req.action_type,
    )
    return MitigationExecutionResponse(
        success=True,
        message=f"Mitigation playbook '{req.action_type.value}' successfully executed by {current_user.email}.",
        incident=SecurityIncidentSchema(**incident.model_dump()),
    )


@router.get("/mitre-matrix", response_model=MitreMatrixResponse)
def get_mitre_attack_matrix(
    current_user: User = Depends(get_current_user),
):
    """Retrieve active threats and detection rules mapped to the MITRE ATT&CK Enterprise Matrix."""
    mappings = EnterpriseSecurityEngine.get_mitre_matrix()
    return MitreMatrixResponse(
        total_tactics_mapped=len(mappings),
        mappings=[MitreAttackMappingSchema(**m.model_dump()) for m in mappings],
    )
