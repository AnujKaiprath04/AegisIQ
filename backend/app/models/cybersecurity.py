from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base


class SecurityIncident(Base):
    __tablename__ = "security_incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g. "SEC-2026-0841"
    title = Column(String(200), nullable=False)
    severity = Column(String(30), default="MEDIUM", index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category = Column(String(50), nullable=False, index=True)  # BRUTE_FORCE_ATTEMPT, ANOMALOUS_GEOLOCATION, PRIVILEGE_ESCALATION, EXCESSIVE_RATE_LIMIT, DATA_EXFILTRATION_SPIKE
    status = Column(String(30), default="OPEN", index=True)  # OPEN, INVESTIGATING, MITIGATED, RESOLVED, FALSE_POSITIVE
    
    actor_ip = Column(String(100), nullable=True)
    actor_email = Column(String(150), nullable=True)
    location_country = Column(String(100), nullable=True)
    event_count = Column(Integer, default=1)
    description = Column(Text, nullable=False)
    mitigation_action_taken = Column(String(100), nullable=True)
    
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    assigned_to = relationship("User")

    def __repr__(self):
        return f"<SecurityIncident(code='{self.incident_code}', severity='{self.severity}', status='{self.status}')>"


class IPBlocklistEntry(Base):
    __tablename__ = "ip_blocklist_entries"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(100), unique=True, nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    is_permanent = Column(Boolean, default=False)
    blocked_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<IPBlocklistEntry(ip='{self.ip_address}', reason='{self.reason}')>"


class ZeroTrustScorecard(Base):
    __tablename__ = "zero_trust_scorecards"

    id = Column(Integer, primary_key=True, index=True)
    overall_risk_score = Column(Float, default=12.0)  # 0 to 100 (Lower is better / safer)
    risk_level = Column(String(30), default="OPTIMAL")  # OPTIMAL, ELEVATED, HIGH_RISK
    auth_entropy_score = Column(Float, default=99.4)  # 0 to 100 (Higher is better)
    rbac_enclosure_score = Column(Float, default=100.0)
    encryption_score = Column(Float, default=100.0)
    anomaly_defense_score = Column(Float, default=98.2)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<ZeroTrustScorecard(score={self.overall_risk_score}, level='{self.risk_level}')>"
