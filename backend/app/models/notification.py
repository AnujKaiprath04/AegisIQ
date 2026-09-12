from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class NotificationItem(Base):
    __tablename__ = "notification_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # Null = Broadcast to all
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="SYSTEM", index=True)  # SECURITY, FINANCIAL, DATA_QUALITY, CHURN_ALERT, SYSTEM
    severity = Column(String(30), default="INFO", index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    is_read = Column(Boolean, default=False, index=True)
    action_url = Column(String(255), nullable=True)
    delivery_channel = Column(String(50), default="IN_APP")  # IN_APP, EMAIL, WEBHOOK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<NotificationItem(title='{self.title}', category='{self.category}', is_read={self.is_read})>"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    trigger_event = Column(String(50), nullable=False, index=True)  # KPI_VARIANCE_BREACH, SECURITY_INCIDENT_HIGH, ETL_QUALITY_DROP, HIGH_CHURN_RISK, REPORT_READY
    threshold_condition = Column(String(255), nullable=False)  # e.g. "Variance > 10.0%", "Quality < 95%"
    severity = Column(String(30), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    
    channel_in_app = Column(Boolean, default=True)
    channel_email = Column(Boolean, default=False)
    channel_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<AlertRule(name='{self.name}', active={self.is_active})>"


class WebhookDeliveryLog(Base):
    __tablename__ = "webhook_delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    target_url = Column(String(500), nullable=False)
    payload_json = Column(Text, nullable=False)
    response_status_code = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    delivered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<WebhookDeliveryLog(url='{self.target_url}', status={self.response_status_code})>"
