from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_format = Column(String(20), nullable=False, default="csv")  # csv, xlsx, json
    storage_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, default=0)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    source_type = Column(String(50), default="FILE_UPLOAD")  # FILE_UPLOAD, ENTERPRISE_SEED, API_SYNC
    schema_json = Column(Text, nullable=True)  # JSON representation of column names and inferred types
    quality_score = Column(Float, default=100.0)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    etl_runs = relationship("ETLPipelineRun", back_populates="dataset", cascade="all, delete-orphan")
    quality_reports = relationship("DataQualityReport", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(name='{self.name}', format='{self.file_format}', rows={self.row_count})>"


class ETLPipelineRun(Base):
    __tablename__ = "etl_pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    run_name = Column(String(150), nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, RUNNING, SUCCESS, FAILED
    config_json = Column(Text, nullable=True)  # JSON config: imputation, deduplication, outlier clipping
    rows_before = Column(Integer, default=0)
    rows_after = Column(Integer, default=0)
    execution_duration_ms = Column(Integer, default=0)
    log_output = Column(Text, nullable=True)
    executed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="etl_runs")
    executed_by = relationship("User", foreign_keys=[executed_by_user_id])

    def __repr__(self):
        return f"<ETLPipelineRun(name='{self.run_name}', status='{self.status}')>"


class DataQualityReport(Base):
    __tablename__ = "data_quality_reports"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    completeness_score = Column(Float, default=100.0)
    uniqueness_score = Column(Float, default=100.0)
    validity_score = Column(Float, default=100.0)
    consistency_score = Column(Float, default=100.0)
    overall_score = Column(Float, default=100.0)
    metrics_json = Column(Text, nullable=True)  # Detailed per-column breakdown
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="quality_reports")

    def __repr__(self):
        return f"<DataQualityReport(dataset_id={self.dataset_id}, score={self.overall_score})>"
