from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base


class MLModelRegistry(Base):
    __tablename__ = "ml_model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(150), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # TIME_SERIES_FORECAST, CHURN_CLASSIFICATION, DEMAND_PREDICTION
    algorithm = Column(String(100), nullable=False)  # EXPONENTIAL_SMOOTHING, RANDOM_FOREST, RIDGE_REGRESSION, PROPHET
    status = Column(String(30), default="TRAINED")  # TRAINED, TRAINING, OUTDATED
    accuracy_score = Column(Float, default=0.0)  # R2 score or ROC-AUC
    mae_metric = Column(Float, default=0.0)
    rmse_metric = Column(Float, default=0.0)
    features_used_json = Column(Text, nullable=True)
    last_trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    predictions = relationship("ForecastPrediction", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MLModelRegistry(name='{self.model_name}', type='{self.model_type}', score={self.accuracy_score})>"


class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_model_registry.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_period = Column(String(50), nullable=False, index=True)  # e.g. "2026-Q2", "2026-Q3", "2026-07"
    predicted_value = Column(Float, nullable=False)
    lower_bound_95 = Column(Float, nullable=False)
    upper_bound_95 = Column(Float, nullable=False)
    metric_name = Column(String(50), default="ARR_USD")  # ARR_USD, REVENUE_USD, INVENTORY_UNITS
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    model = relationship("MLModelRegistry", back_populates="predictions")

    def __repr__(self):
        return f"<ForecastPrediction(period='{self.forecast_period}', pred={self.predicted_value})>"


class CustomerChurnPrediction(Base):
    __tablename__ = "customer_churn_predictions"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(150), nullable=False, index=True)
    account_arr = Column(Float, nullable=False)
    churn_probability_pct = Column(Float, nullable=False)  # 0.0 to 100.0
    risk_tier = Column(String(30), default="LOW_RISK", index=True)  # LOW_RISK, MEDIUM_RISK, HIGH_RISK
    top_risk_factors_json = Column(Text, nullable=True)  # JSON array of strings
    recommended_intervention = Column(Text, nullable=True)
    contract_renewal_date = Column(String(30), nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<CustomerChurnPrediction(client='{self.client_name}', prob={self.churn_probability_pct}%, tier='{self.risk_tier}')>"
