from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.notification import (
    AlertRuleCreate,
    AlertRuleResponse,
    NotificationSummary,
    UnreadCountResponse,
    WebhookDeliveryLogResponse,
    WebhookTestRequest,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Module 14: Real-time Multi-Channel Notifications"])


@router.get("", response_model=List[NotificationSummary])
def list_notifications(
    category: Optional[str] = Query("ALL", description="Filter by category: SECURITY, FINANCIAL, DATA_QUALITY, CHURN_ALERT, SYSTEM, ALL"),
    unread_only: bool = Query(False, description="Filter only unread items"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-channel enterprise notifications and system broadcasts."""
    return NotificationService.get_notifications(db=db, category=category, unread_only=unread_only)


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fast unread notification counter for top navigation bar badge."""
    return NotificationService.get_unread_count(db=db)


@router.post("/{notification_id}/read", response_model=NotificationSummary)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an individual notification item as read."""
    return NotificationService.mark_as_read(db=db, notification_id=notification_id)


@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all active unread notifications as read in a single batch."""
    return NotificationService.mark_all_as_read(db=db)


@router.get("/rules", response_model=List[AlertRuleResponse])
def list_alert_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List configured automated alert trigger rules and multi-channel routing settings."""
    return NotificationService.get_alert_rules(db=db)


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    req: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Create a new automated threshold alert trigger rule."""
    return NotificationService.create_alert_rule(db=db, req=req, user=current_user)


@router.post("/rules/{rule_id}/toggle", response_model=AlertRuleResponse)
def toggle_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Enable or disable an automated alert rule."""
    return NotificationService.toggle_alert_rule(db=db, rule_id=rule_id)


@router.post("/webhook/test", response_model=WebhookDeliveryLogResponse)
def test_webhook_dispatch(
    req: WebhookTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Test webhook delivery link to external receptor (Slack, Teams, PagerDuty)."""
    return NotificationService.test_webhook_dispatch(db=db, req=req)
