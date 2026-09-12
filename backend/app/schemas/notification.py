from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NotificationSummary(BaseModel):
    id: int
    title: str
    message: str
    category: str  # SECURITY, FINANCIAL, DATA_QUALITY, CHURN_ALERT, SYSTEM
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    is_read: bool
    action_url: Optional[str] = None
    delivery_channel: str
    created_at: datetime

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    unread_count: int


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    trigger_event: str = Field(..., description="KPI_VARIANCE_BREACH, SECURITY_INCIDENT_HIGH, ETL_QUALITY_DROP, HIGH_CHURN_RISK, REPORT_READY")
    threshold_condition: str = Field(..., description="e.g. Variance > 10%, Quality < 95%")
    severity: str = "HIGH"
    channel_in_app: bool = True
    channel_email: bool = False
    channel_webhook: bool = False
    webhook_url: Optional[str] = None


class AlertRuleResponse(AlertRuleCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookTestRequest(BaseModel):
    webhook_url: str = Field(..., min_length=10, description="Target Slack / MS Teams / Custom HTTP webhook endpoint")
    channel_name: Optional[str] = "Slack Alert Relay"


class WebhookDeliveryLogResponse(BaseModel):
    target_url: str
    response_status_code: int
    response_body: str
    latency_ms: float
    delivered_at: datetime
