from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.alert_engine.types import (
    AlertChannel,
    AlertIncident,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    AlertTriggerSource,
)


class AlertRuleSchema(AlertRule):
    pass


class AlertIncidentSchema(AlertIncident):
    pass


class AlertRulesListResponse(BaseModel):
    total_rules: int
    rules: List[AlertRuleSchema] = []


class AlertIncidentsListResponse(BaseModel):
    total_incidents: int
    incidents: List[AlertIncidentSchema] = []


class AlertDispatchRequest(BaseModel):
    rule_id: str = Field(default="RULE-CHURN-001")
    title: str
    description: str
    severity: AlertSeverity = AlertSeverity.CRITICAL
    target_entity: str
    trigger_source: AlertTriggerSource = AlertTriggerSource.PREDICTION_CHURN
    override_channels: Optional[List[AlertChannel]] = None


class AlertDispatchResponse(BaseModel):
    incident: AlertIncidentSchema


class AlertActionResponse(BaseModel):
    success: bool
    message: str
    incident: AlertIncidentSchema
