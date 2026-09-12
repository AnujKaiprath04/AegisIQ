from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    name: str
    data_type: str  # numeric, text, datetime, boolean
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any] = []
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None


class DatasetSummary(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    file_format: str
    file_size_bytes: int
    row_count: int
    column_count: int
    source_type: str
    quality_score: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatasetDetail(DatasetSummary):
    schema_json: Optional[str] = None
    columns: List[ColumnMetadata] = []


class DatasetPreview(BaseModel):
    id: int
    name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    preview_limit: int


class DatasetUploadResponse(BaseModel):
    message: str
    dataset: DatasetSummary
