from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.report_generator import (
    ExecutiveReportResponse,
    GenerateReportRequest,
    ReportHistoryListResponse,
    ReportTemplateInfo,
)
from app.report_service.generator import ExecutiveReportGenerator
from app.report_service.types import ReportFormat, ReportType

router = APIRouter(prefix="/ai/reports", tags=["Part 2 - Module 11: Executive Report Generator"])


@router.get("/templates", response_model=List[ReportTemplateInfo])
def list_report_templates(
    current_user: User = Depends(get_current_user),
):
    """List available standardized executive report templates and supported output formats."""
    templates = ExecutiveReportGenerator.list_templates()
    return [ReportTemplateInfo(**t) for t in templates]


@router.post("/generate", response_model=ExecutiveReportResponse)
def generate_executive_report(
    req: GenerateReportRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Synthesize cross-domain enterprise metrics and generate boardroom executive briefings."""
    report = ExecutiveReportGenerator.generate_report(
        report_type=req.report_type or ReportType.BOARDROOM_QUARTERLY_BRIEF,
        period=req.period or "Q1 2026",
        report_format=req.format or ReportFormat.MARKDOWN,
        author=current_user.full_name or "AegisIQ Executive Intelligence Engine",
    )
    return ExecutiveReportResponse(**report.model_dump())


@router.get("/history", response_model=ReportHistoryListResponse)
def list_report_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """List previously compiled executive reports and boardroom briefings from the archive."""
    reports = ExecutiveReportGenerator.list_history(limit=limit)
    return ReportHistoryListResponse(
        total_reports=len(reports),
        reports=[ExecutiveReportResponse(**r.model_dump()) for r in reports],
    )


@router.get("/{report_id}", response_model=ExecutiveReportResponse)
def get_report_by_id(
    report_id: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve full compiled executive report and rendered Markdown/HTML content by ID."""
    report = ExecutiveReportGenerator.get_report(report_id)
    return ExecutiveReportResponse(**report.model_dump())
