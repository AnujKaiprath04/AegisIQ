from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ETLConfig(BaseModel):
    dataset_id: int
    pipeline_name: Optional[str] = "Standard Quality & Cleaning Pipeline"
    remove_duplicates: bool = True
    handle_missing: bool = True
    missing_strategy: str = Field("auto", description="auto, mean, median, mode, drop, ffill")
    handle_outliers: bool = True
    outlier_method: str = Field("iqr", description="iqr or zscore")
    outlier_action: str = Field("clip", description="clip or drop")
    standardize_headers: bool = True


class ETLRunResponse(BaseModel):
    id: int
    dataset_id: int
    run_name: str
    status: str
    rows_before: int
    rows_after: int
    execution_duration_ms: int
    log_output: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PillarScore(BaseModel):
    score: float
    status: str  # EXCELLENT, GOOD, WARNING, CRITICAL
    issues_found: int
    details: str


class DataQualityReportResponse(BaseModel):
    dataset_id: int
    dataset_name: str
    overall_score: float
    completeness: PillarScore
    uniqueness: PillarScore
    validity: PillarScore
    consistency: PillarScore
    columns_analyzed: int
    rows_analyzed: int
    generated_at: datetime
    column_breakdown: List[Dict[str, Any]] = []
