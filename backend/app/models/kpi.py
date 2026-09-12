from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., GROSS_MARGIN, CAC, LTV_CAC
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # FINANCIAL, SALES, OPERATIONS, CUSTOMERS
    description = Column(Text, nullable=True)
    formula_expression = Column(String(255), nullable=True)
    unit = Column(String(20), default="")  # %, $, ratio, days, count
    current_value = Column(Float, default=0.0)
    target_value = Column(Float, default=0.0)
    benchmark_value = Column(Float, nullable=True)
    variance_pct = Column(Float, default=0.0)
    trend_direction = Column(String(10), default="UP")  # UP, DOWN, NEUTRAL
    status = Column(String(20), default="ON_TRACK")  # ON_TRACK, WARNING, CRITICAL
    period = Column(String(50), default="Q1 2026")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<KPIMetric(code='{self.code}', current={self.current_value}, target={self.target_value})>"


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)  # EXECUTIVE_SUMMARY, FINANCIAL_HEALTH, OPERATIONAL_AUDIT, DATA_QUALITY
    format = Column(String(20), nullable=False, default="PDF")  # PDF, EXCEL, CSV
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    parameters_json = Column(Text, nullable=True)
    generated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    generated_by = relationship("User", foreign_keys=[generated_by_user_id])

    def __repr__(self):
        return f"<GeneratedReport(title='{self.title}', format='{self.format}')>"
