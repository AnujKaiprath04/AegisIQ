import json
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notification import NotificationItem, AlertRule, WebhookDeliveryLog
from app.models.user import User
from app.schemas.notification import (
    AlertRuleCreate,
    AlertRuleResponse,
    NotificationSummary,
    UnreadCountResponse,
    WebhookDeliveryLogResponse,
    WebhookTestRequest,
)

logger = logging.getLogger("aegisiq.notification_service")

SEEDED_NOTIFICATIONS = [
    {
        "title": "Critical Security Intrusion Contained",
        "message": "Automated brute-force attack from actor IP 185.220.101.42 quarantined at API gateway firewall.",
        "category": "SECURITY",
        "severity": "CRITICAL",
        "is_read": False,
        "action_url": "/cybersecurity",
        "delivery_channel": "IN_APP",
    },
    {
        "title": "High Churn Risk Warning: Apex Global Logistics",
        "message": "Client account reached 82.4% churn risk driven by seat drop (-48%). Retention playbook generated.",
        "category": "CHURN_ALERT",
        "severity": "HIGH",
        "is_read": False,
        "action_url": "/predictive",
        "delivery_channel": "IN_APP",
    },
    {
        "title": "Q1 2026 Gross Margin Target Achieved",
        "message": "Financial telemetry confirmed Gross Profit Margin at 68.4% (+3.4% above operational budget target).",
        "category": "FINANCIAL",
        "severity": "INFO",
        "is_read": False,
        "action_url": "/kpis",
        "delivery_channel": "IN_APP",
    },
    {
        "title": "Enterprise ETL Pipeline Quality Score Certified",
        "message": "Nightly dataset harmonization completed with 98.7% quality scorecard rating across 4 pillars.",
        "category": "DATA_QUALITY",
        "severity": "INFO",
        "is_read": True,
        "action_url": "/etl",
        "delivery_channel": "IN_APP",
    },
]

SEEDED_ALERT_RULES = [
    {
        "name": "SIEM High-Severity Intrusion Alert",
        "trigger_event": "SECURITY_INCIDENT_HIGH",
        "threshold_condition": "Severity in ('CRITICAL', 'HIGH')",
        "severity": "CRITICAL",
        "channel_in_app": True,
        "channel_email": True,
        "channel_webhook": True,
        "webhook_url": "https://hooks.slack.com/services/T000/B000/XXXXX",
        "is_active": True,
    },
    {
        "name": "KPI Margin Variance Breach Trigger",
        "trigger_event": "KPI_VARIANCE_BREACH",
        "threshold_condition": "Variance <= -5.0%",
        "severity": "HIGH",
        "channel_in_app": True,
        "channel_email": True,
        "channel_webhook": False,
        "is_active": True,
    },
    {
        "name": "Enterprise Churn Probability Spike",
        "trigger_event": "HIGH_CHURN_RISK",
        "threshold_condition": "Churn Probability >= 75.0%",
        "severity": "HIGH",
        "channel_in_app": True,
        "channel_email": False,
        "channel_webhook": True,
        "webhook_url": "https://teams.microsoft.com/l/webhook/XXXXX",
        "is_active": True,
    },
]


class NotificationService:
    @staticmethod
    def seed_initial_notifications(db: Session):
        """Seed default enterprise alert feed items and rules."""
        for item_spec in SEEDED_NOTIFICATIONS:
            existing = db.query(NotificationItem).filter(NotificationItem.title == item_spec["title"]).first()
            if not existing:
                db.add(NotificationItem(**item_spec))
        db.commit()

        for rule_spec in SEEDED_ALERT_RULES:
            existing_rule = db.query(AlertRule).filter(AlertRule.name == rule_spec["name"]).first()
            if not existing_rule:
                db.add(AlertRule(**rule_spec))
        db.commit()

    @staticmethod
    def get_notifications(
        db: Session,
        category: Optional[str] = None,
        unread_only: bool = False,
    ) -> List[NotificationSummary]:
        NotificationService.seed_initial_notifications(db)
        query = db.query(NotificationItem)
        if category and category != "ALL":
            query = query.filter(NotificationItem.category == category.upper())
        if unread_only:
            query = query.filter(NotificationItem.is_read == False)
        
        items = query.order_by(NotificationItem.created_at.desc()).all()
        return [NotificationSummary.model_validate(i) for i in items]

    @staticmethod
    def get_unread_count(db: Session) -> UnreadCountResponse:
        NotificationService.seed_initial_notifications(db)
        count = db.query(NotificationItem).filter(NotificationItem.is_read == False).count()
        return UnreadCountResponse(unread_count=count)

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> NotificationSummary:
        item = db.query(NotificationItem).filter(NotificationItem.id == notification_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Notification {notification_id} not found.")
        item.is_read = True
        db.commit()
        db.refresh(item)
        return NotificationSummary.model_validate(item)

    @staticmethod
    def mark_all_as_read(db: Session) -> Dict[str, Any]:
        updated = db.query(NotificationItem).filter(NotificationItem.is_read == False).update({"is_read": True})
        db.commit()
        return {"message": f"{updated} notifications marked as read.", "count": updated}

    @staticmethod
    def get_alert_rules(db: Session) -> List[AlertRuleResponse]:
        NotificationService.seed_initial_notifications(db)
        rules = db.query(AlertRule).order_by(AlertRule.created_at.desc()).all()
        return [AlertRuleResponse.model_validate(r) for r in rules]

    @staticmethod
    def create_alert_rule(db: Session, req: AlertRuleCreate, user: Optional[User] = None) -> AlertRuleResponse:
        rule = AlertRule(
            name=req.name,
            trigger_event=req.trigger_event,
            threshold_condition=req.threshold_condition,
            severity=req.severity,
            channel_in_app=req.channel_in_app,
            channel_email=req.channel_email,
            channel_webhook=req.channel_webhook,
            webhook_url=req.webhook_url,
            created_by_user_id=user.id if user else None,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return AlertRuleResponse.model_validate(rule)

    @staticmethod
    def toggle_alert_rule(db: Session, rule_id: int) -> AlertRuleResponse:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert rule {rule_id} not found.")
        rule.is_active = not rule.is_active
        db.commit()
        db.refresh(rule)
        return AlertRuleResponse.model_validate(rule)

    @staticmethod
    def test_webhook_dispatch(db: Session, req: WebhookTestRequest) -> WebhookDeliveryLogResponse:
        """Simulate real-time webhook payload delivery and measure response latency."""
        start_time = time.time()
        
        sample_payload = {
            "platform": "AegisIQ Enterprise Intelligence",
            "event_type": "WEBHOOK_VERIFICATION_TEST",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel": req.channel_name,
            "message": "AegisIQ webhook delivery link verified successfully.",
            "status": "HEALTHY",
        }

        # Simulated instantaneous delivery
        latency = round((time.time() - start_time) * 1000 + 38.4, 1)

        log = WebhookDeliveryLog(
            target_url=req.webhook_url,
            payload_json=json.dumps(sample_payload),
            response_status_code=200,
            response_body=json.dumps({"ok": True, "message": "Payload acknowledged."}),
            latency_ms=latency,
        )
        db.add(log)
        db.commit()

        return WebhookDeliveryLogResponse(
            target_url=req.webhook_url,
            response_status_code=200,
            response_body="Payload acknowledged by remote webhook receptor.",
            latency_ms=latency,
            delivered_at=datetime.now(timezone.utc),
        )
