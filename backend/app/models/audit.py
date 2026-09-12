from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # Snapshot in case user is deleted
    action = Column(String(100), nullable=False, index=True)  # e.g., LOGIN_SUCCESS, ROLE_UPDATED
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    status = Column(String(20), default="SUCCESS")  # SUCCESS, FAILED, WARNING
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship
    user = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<UserActivityLog(action='{self.action}', status='{self.status}', user_email='{self.user_email}')>"
