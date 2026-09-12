from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertChannel(str, Enum):
    SLACK = "SLACK"
    MICROSOFT_TEAMS = "MICROSOFT_TEAMS"
    WEBHOOK = "WEBHOOK"
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class AlertStatus(str, Enum):
    TRIGGERED = "TRIGGERED"
    DISPATCHED = "DISPATCHED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    SUPPRESSED_DUPLICATE = "SUPPRESSED_DUPLICATE"


class AlertTriggerSource(str, Enum):
    PREDICTION_CHURN = "PREDICTION_CHURN"
    PREDICTION_REVENUE = "PREDICTION_REVENUE"
    CYBERSECURITY_SIEM = "CYBERSECURITY_SIEM"
    ANOMALY_OUTLIER = "ANOMALY_OUTLIER"
    BUSINESS_RISK = "BUSINESS_RISK"


class AlertRule(BaseModel):
    rule_id: str
    name: str
    trigger_source: AlertTriggerSource
    condition_metric: str
    threshold: float
    target_channels: List[AlertChannel] = [AlertChannel.SLACK, AlertChannel.IN_APP]
    escalation_enabled: bool = True
    dedup_window_minutes: int = 15
    is_active: bool = True


class AlertIncident(BaseModel):
    incident_id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    trigger_source: AlertTriggerSource
    status: AlertStatus
    dispatched_channels: List[AlertChannel] = []
    target_entity: str
    current_escalation_tier: int = Field(default=1, ge=1, le=3)
    channel_payloads: Dict[str, Any] = {}
    triggered_at: str
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
