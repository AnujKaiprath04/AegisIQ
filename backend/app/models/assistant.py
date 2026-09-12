from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    persona = Column(String(50), default="CEO_STRATEGIST", index=True)  # CEO_STRATEGIST, CFO_FINANCIAL, CTO_ARCHITECT, BI_ANALYST, SECURITY_OFFICER
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.id.asc()")

    def __repr__(self):
        return f"<AIConversation(title='{self.title}', persona='{self.persona}')>"


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Transparency & Data Verification
    generated_sql = Column(Text, nullable=True)
    data_results_json = Column(Text, nullable=True)
    citations_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")

    def __repr__(self):
        return f"<AIMessage(role='{self.role}', tokens={self.tokens_used})>"
