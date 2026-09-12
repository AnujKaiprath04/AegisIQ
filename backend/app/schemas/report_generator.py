from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.report_service.types import (
    ExecutiveReportPayload,
    ReportFormat,
    ReportSection,
    ReportType,
)


class ReportTemplateInfo(BaseModel):
    type: str
    title: str
    description: str
    target_audience: str
    supported_formats: List[str] = []


class GenerateReportRequest(BaseModel):
    report_type: Optional[ReportType] = ReportType.BOARDROOM_QUARTERLY_BRIEF
    period: Optional[str] = Field(default="Q1 2026", min_length=2, max_length=50)
    format: Optional[ReportFormat] = ReportFormat.MARKDOWN


class ExecutiveReportResponse(BaseModel):
    report_id: str
    report_type: ReportType
    title: str
    period: str
    generated_at: str
    author: str
    executive_summary: str
    sections: List[ReportSection] = []
    recommendations: List[Dict[str, Any]] = []
    rendered_content: str
    format: ReportFormat


class ReportHistoryListResponse(BaseModel):
    total_reports: int
    reports: List[ExecutiveReportResponse] = []
