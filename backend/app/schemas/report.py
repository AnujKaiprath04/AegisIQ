from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    report_type: str = Field("EXECUTIVE_SUMMARY", description="EXECUTIVE_SUMMARY, FINANCIAL_HEALTH, OPERATIONAL_AUDIT, DATA_QUALITY")
    format: str = Field("PDF", description="PDF, EXCEL, CSV")
    dataset_id: Optional[int] = None
    date_range: Optional[str] = "Q1 2026"
    include_charts: bool = True
    executive_summary_notes: Optional[str] = None


class GeneratedReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    format: str
    file_size_bytes: int
    parameters_json: Optional[str] = None
    created_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    reports: List[GeneratedReportResponse]
    total_count: int
