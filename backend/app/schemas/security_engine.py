from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.security_engine.types import (
    IncidentStatus,
    MitreAttackMapping,
    SecurityActionType,
    SecurityIncident,
    SecurityPostureSummary,
    ThreatSeverity,
    ThreatVectorType,
)


class SecurityIncidentSchema(SecurityIncident):
    pass


class SecurityPostureSummarySchema(SecurityPostureSummary):
    pass


class MitreAttackMappingSchema(MitreAttackMapping):
    pass


class ThreatEventAnalysisRequest(BaseModel):
    event_type: ThreatVectorType
    payload: Dict[str, Any] = Field(default_factory=dict)


class MitigationExecutionRequest(BaseModel):
    action_type: SecurityActionType = SecurityActionType.EDGE_IP_QUARANTINE


class MitigationExecutionResponse(BaseModel):
    success: bool
    message: str
    incident: SecurityIncidentSchema


class SecurityIncidentListResponse(BaseModel):
    total_incidents: int
    incidents: List[SecurityIncidentSchema] = []


class MitreMatrixResponse(BaseModel):
    total_tactics_mapped: int
    mappings: List[MitreAttackMappingSchema] = []
