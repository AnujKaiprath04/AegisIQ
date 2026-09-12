from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class XAIExplanationSession(Base):
    __tablename__ = "xai_explanation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50), default="CHURN_CLASSIFICATION", index=True)
    target_entity_id = Column(Integer, nullable=False, index=True)
    entity_name = Column(String(150), nullable=False)
    base_value = Column(Float, nullable=False)  # Expected base value E[f(x)]
    predicted_value = Column(Float, nullable=False)  # Final f(x)
    explanation_method = Column(String(50), default="SHAP_KERNEL")  # SHAP_KERNEL, TREE_SHAP, LIME
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    contributions = relationship("XAIFeatureContribution", back_populates="session", cascade="all, delete-orphan", order_by="XAIFeatureContribution.importance_rank.asc()")

    def __repr__(self):
        return f"<XAIExplanationSession(entity='{self.entity_name}', pred={self.predicted_value})>"


class XAIFeatureContribution(Base):
    __tablename__ = "xai_feature_contributions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("xai_explanation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(150), nullable=False)
    feature_value = Column(String(100), nullable=False)
    shap_value = Column(Float, nullable=False)  # e.g. +0.28, -0.12
    contribution_direction = Column(String(30), nullable=False)  # INCREASES_RISK, DECREASES_RISK
    importance_rank = Column(Integer, default=1)

    # Relationships
    session = relationship("XAIExplanationSession", back_populates="contributions")

    def __repr__(self):
        return f"<XAIFeatureContribution(feature='{self.feature_name}', shap={self.shap_value})>"


class WhatIfSimulationLog(Base):
    __tablename__ = "whatif_simulation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    model_type = Column(String(50), default="CHURN_CLASSIFICATION")
    original_prediction = Column(Float, nullable=False)
    simulated_prediction = Column(Float, nullable=False)
    modified_features_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<WhatIfSimulationLog(orig={self.original_prediction}, sim={self.simulated_prediction})>"
