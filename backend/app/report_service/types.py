from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    BOARDROOM_QUARTERLY_BRIEF = "BOARDROOM_QUARTERLY_BRIEF"
    FINANCIAL_OPERATIONAL_REVIEW = "FINANCIAL_OPERATIONAL_REVIEW"
    CYBERSECURITY_COMPLIANCE_POSTURE = "CYBERSECURITY_COMPLIANCE_POSTURE"
    DATA_PLATFORM_HEALTH_AUDIT = "DATA_PLATFORM_HEALTH_AUDIT"


class ReportFormat(str, Enum):
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    JSON = "JSON"


class ReportSection(BaseModel):
    title: str
    order: int
    key_metrics: Dict[str, Any] = {}
    narrative_summary: str
    bullet_points: List[str] = []


class ExecutiveReportPayload(BaseModel):
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
