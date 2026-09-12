from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = None
    connection_type: str = Field(..., description="POSTGRESQL, MYSQL, SQLITE, MONGODB, REST_API, FILE_STORAGE")
    
    # DB fields
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    ssl_enabled: bool = True

    # REST API fields
    api_endpoint_url: Optional[str] = None
    api_auth_type: str = "NONE"  # NONE, BEARER_TOKEN, API_KEY, BASIC
    api_headers_json: Optional[str] = None


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    ssl_enabled: Optional[bool] = None
    api_endpoint_url: Optional[str] = None
    api_auth_type: Optional[str] = None
    api_headers_json: Optional[str] = None
    status: Optional[str] = None


class ConnectionTestResult(BaseModel):
    connection_id: Optional[int] = None
    success: bool
    status: str  # ACTIVE, UNREACHABLE, DEGRADED
    latency_ms: float
    message: str
    server_version: Optional[str] = None
    ssl_verified: bool = True
    tested_at: datetime


class MetadataCatalogColumnResponse(BaseModel):
    id: int
    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    sample_values: List[Any] = []

    class Config:
        from_attributes = True


class MetadataCatalogTableResponse(BaseModel):
    id: int
    connection_id: int
    table_name: str
    schema_name: str
    table_type: str
    estimated_row_count: int
    column_count: int
    primary_key_columns: Optional[str] = None
    columns: List[MetadataCatalogColumnResponse] = []
    discovered_at: datetime

    class Config:
        from_attributes = True


class ConnectionSummary(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    connection_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    api_endpoint_url: Optional[str] = None
    status: str
    latency_ms: float
    ssl_enabled: bool
    last_tested_at: Optional[datetime] = None
    tables_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class SchemaTreeResponse(BaseModel):
    connection_id: int
    connection_name: str
    connection_type: str
    database_name: Optional[str] = None
    tables: List[MetadataCatalogTableResponse] = []
    total_tables: int
    total_columns: int


class IngestionJobCreate(BaseModel):
    connection_id: int
    table_id: Optional[int] = None
    job_name: str = Field(..., min_length=3, max_length=150)
    sync_mode: str = Field("FULL_SYNC", description="FULL_SYNC, INCREMENTAL_WATERMARK, SNAPSHOT")
    sync_schedule: str = Field("MANUAL", description="HOURLY, DAILY, WEEKLY, MANUAL")


class IngestionJobResponse(BaseModel):
    id: int
    connection_id: int
    table_id: Optional[int] = None
    job_name: str
    sync_mode: str
    sync_schedule: str
    status: str
    rows_ingested: int
    bytes_transferred: int
    duration_seconds: float
    error_log: Optional[str] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobRunTriggerResponse(BaseModel):
    job_id: int
    status: str
    rows_ingested: int
    duration_seconds: float
    message: str
