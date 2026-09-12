import os
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.report import (
    GeneratedReportResponse,
    ReportGenerateRequest,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Automated Report Generator"])


@router.get("", response_model=List[GeneratedReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """List all previously generated executive reports and export files."""
    reports = ReportService.get_reports(db=db)
    return [
        GeneratedReportResponse(
            id=r.id,
            title=r.title,
            report_type=r.report_type,
            format=r.format,
            file_size_bytes=r.file_size_bytes,
            parameters_json=r.parameters_json,
            created_at=r.created_at,
            download_url=f"/api/v1/reports/{r.id}/download",
        )
        for r in reports
    ]


@router.post("/generate", response_model=GeneratedReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst"])),
):
    """Generate on-demand PDF executive brief, formatted Excel workbook, or CSV export."""
    report = ReportService.create_report(db=db, req=req, user=current_user)
    return GeneratedReportResponse(
        id=report.id,
        title=report.title,
        report_type=report.report_type,
        format=report.format,
        file_size_bytes=report.file_size_bytes,
        parameters_json=report.parameters_json,
        created_at=report.created_at,
        download_url=f"/api/v1/reports/{report.id}/download",
    )


@router.get("/{report_id}/download")
def download_report_file(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Business Analyst", "Data Analyst", "Viewer"])),
):
    """Directly stream and download generated report file (PDF, XLSX, CSV)."""
    report = ReportService.get_report_by_id(db=db, report_id=report_id)
    if not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested report file is no longer available on disk.",
        )

    media_type = "application/pdf" if report.format == "PDF" else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if report.format == "EXCEL" else "text/csv"
    )
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename,
    )
