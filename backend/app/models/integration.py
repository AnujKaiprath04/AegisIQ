from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, Float, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base


class DataConnection(Base):
    __tablename__ = "data_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    connection_type = Column(String(50), nullable=False)  # POSTGRESQL, MYSQL, SQLITE, MONGODB, REST_API, FILE_STORAGE
    
    # DB Parameters
    host = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    database_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    encrypted_password = Column(String(255), nullable=True)
    connection_string = Column(String(500), nullable=True)
    ssl_enabled = Column(Boolean, default=True)

    # REST API Parameters
    api_endpoint_url = Column(String(500), nullable=True)
    api_auth_type = Column(String(50), default="NONE")  # NONE, BEARER_TOKEN, API_KEY, BASIC
    api_headers_json = Column(Text, nullable=True)

    # Health & Diagnostics
    status = Column(String(30), default="ACTIVE")  # ACTIVE, INACTIVE, UNREACHABLE, DEGRADED
    latency_ms = Column(Float, default=0.0)
    last_tested_at = Column(DateTime, nullable=True)
    
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    catalog_tables = relationship("MetadataCatalogTable", back_populates="connection", cascade="all, delete-orphan")
    ingestion_jobs = relationship("IngestionJob", back_populates="connection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DataConnection(name='{self.name}', type='{self.connection_type}', status='{self.status}')>"


class MetadataCatalogTable(Base):
    __tablename__ = "metadata_catalog_tables"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("data_connections.id", ondelete="CASCADE"), nullable=False, index=True)
    table_name = Column(String(150), nullable=False, index=True)
    schema_name = Column(String(100), default="public")
    table_type = Column(String(50), default="TABLE")  # TABLE, VIEW, COLLECTION, ENDPOINT
    estimated_row_count = Column(BigInteger, default=0)
    column_count = Column(Integer, default=0)
    primary_key_columns = Column(String(255), nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    connection = relationship("DataConnection", back_populates="catalog_tables")
    columns = relationship("MetadataCatalogColumn", back_populates="table", cascade="all, delete-orphan")
    ingestion_jobs = relationship("IngestionJob", back_populates="table")

    def __repr__(self):
        return f"<MetadataCatalogTable(table='{self.table_name}', rows={self.estimated_row_count})>"


class MetadataCatalogColumn(Base):
    __tablename__ = "metadata_catalog_columns"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("metadata_catalog_tables.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(150), nullable=False)
    data_type = Column(String(100), nullable=False)  # VARCHAR, INTEGER, TIMESTAMP, NUMERIC, JSON, etc.
    is_nullable = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    sample_values_json = Column(Text, nullable=True)

    # Relationships
    table = relationship("MetadataCatalogTable", back_populates="columns")

    def __repr__(self):
        return f"<MetadataCatalogColumn(name='{self.column_name}', type='{self.data_type}')>"


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("data_connections.id", ondelete="CASCADE"), nullable=False, index=True)
    table_id = Column(Integer, ForeignKey("metadata_catalog_tables.id", ondelete="SET NULL"), nullable=True)
    job_name = Column(String(150), nullable=False)
    sync_mode = Column(String(50), default="FULL_SYNC")  # FULL_SYNC, INCREMENTAL_WATERMARK, SNAPSHOT
    sync_schedule = Column(String(50), default="MANUAL")  # HOURLY, DAILY, WEEKLY, MANUAL
    status = Column(String(30), default="PENDING")  # PENDING, RUNNING, SUCCESS, FAILED
    rows_ingested = Column(BigInteger, default=0)
    bytes_transferred = Column(BigInteger, default=0)
    duration_seconds = Column(Float, default=0.0)
    error_log = Column(Text, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    connection = relationship("DataConnection", back_populates="ingestion_jobs")
    table = relationship("MetadataCatalogTable", back_populates="ingestion_jobs")

    def __repr__(self):
        return f"<IngestionJob(name='{self.job_name}', status='{self.status}')>"
