from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.alert_engine import (
    AlertActionResponse,
    AlertDispatchRequest,
    AlertDispatchResponse,
    AlertIncidentSchema,
    AlertIncidentsListResponse,
    AlertRuleSchema,
    AlertRulesListResponse,
)
from app.alert_engine.engine import EnterpriseAlertEngine
from app.alert_engine.types import (
    AlertIncident,
    AlertRule,
    AlertSeverity,
    AlertStatus,
)

router = APIRouter(prefix="/ml/alerts", tags=["Part 3 - Module 9: Alert & Notification Engine"])


@router.get("/rules", response_model=AlertRulesListResponse)
def list_alert_rules(
    current_user: User = Depends(get_current_user),
):
    """List configured predictive alert rules and trigger thresholds."""
    rules = EnterpriseAlertEngine.list_rules()
    return AlertRulesListResponse(
        total_rules=len(rules),
        rules=[AlertRuleSchema(**r.model_dump()) for r in rules],
    )


@router.post("/rules", response_model=AlertRuleSchema)
def create_or_update_alert_rule(
    rule: AlertRuleSchema,
    current_user: User = Depends(get_current_user),
):
    """Create or update a predictive trigger alert rule."""
    saved = EnterpriseAlertEngine.create_or_update_rule(rule)
    return AlertRuleSchema(**saved.model_dump())


@router.get("/incidents", response_model=AlertIncidentsListResponse)
def list_alert_incidents(
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
):
    """List alert incidents sorted by timestamp descending."""
    incidents = EnterpriseAlertEngine.list_incidents(
        severity=severity,
        status_filter=status,
    )
    return AlertIncidentsListResponse(
        total_incidents=len(incidents),
        incidents=[AlertIncidentSchema(**i.model_dump()) for i in incidents],
    )


@router.post("/dispatch", response_model=AlertDispatchResponse)
def dispatch_alert(
    req: AlertDispatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Trigger real-time multi-channel alert dispatch with hash deduplication."""
    incident = EnterpriseAlertEngine.dispatch_alert(
        rule_id=req.rule_id,
        title=req.title,
        description=req.description,
        severity=req.severity,
        target_entity=req.target_entity,
        trigger_source=req.trigger_source,
        override_channels=req.override_channels,
    )
    return AlertDispatchResponse(incident=AlertIncidentSchema(**incident.model_dump()))


@router.post("/incidents/{incident_id}/acknowledge", response_model=AlertActionResponse)
def acknowledge_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
):
    """Acknowledge an active alert incident to halt the escalation ladder."""
    inc = EnterpriseAlertEngine.acknowledge_incident(incident_id)
    return AlertActionResponse(
        success=True,
        message=f"Alert incident '{inc.incident_id}' acknowledged by {current_user.email}.",
        incident=AlertIncidentSchema(**inc.model_dump()),
    )


@router.post("/incidents/{incident_id}/resolve", response_model=AlertActionResponse)
def resolve_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
):
    """Mark an alert incident as resolved."""
    inc = EnterpriseAlertEngine.resolve_incident(incident_id)
    return AlertActionResponse(
        success=True,
        message=f"Alert incident '{inc.incident_id}' resolved by {current_user.email}.",
        incident=AlertIncidentSchema(**inc.model_dump()),
    )
