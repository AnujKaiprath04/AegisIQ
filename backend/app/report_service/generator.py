import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.report_service.types import (
    ExecutiveReportPayload,
    ReportFormat,
    ReportSection,
    ReportType,
)
from app.report_service.templates import ReportTemplateRenderer
from app.assistant_service.recommendations import BusinessRecommendationEngine
from app.assistant_service.types import PersonaType

logger = logging.getLogger("aegisiq.report_service")


class ExecutiveReportGenerator:
    """Orchestrates cross-domain enterprise data synthesis and boardroom report generation."""

    _archive: Dict[str, ExecutiveReportPayload] = {}

    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        return [
            {
                "type": ReportType.BOARDROOM_QUARTERLY_BRIEF.value,
                "title": "Board of Directors Quarterly Strategic Brief",
                "description": "Multi-pillar executive report synthesizing ARR growth, unit margins, zero-trust cybersecurity, and SLA uptime.",
                "target_audience": "Board of Directors & C-Suite Executives",
                "supported_formats": ["MARKDOWN", "HTML", "JSON"],
            },
            {
                "type": ReportType.FINANCIAL_OPERATIONAL_REVIEW.value,
                "title": "Executive Financial & Capital Allocation Review",
                "description": "Deep-dive into revenue variance, gross margin expansion, CAC-to-LTV payback, and cash runway pacing.",
                "target_audience": "CFO, VP Finance & Investors",
                "supported_formats": ["MARKDOWN", "HTML", "JSON"],
            },
            {
                "type": ReportType.CYBERSECURITY_COMPLIANCE_POSTURE.value,
                "title": "Enterprise Cybersecurity & ISO 27001 Audit Briefing",
                "description": "Zero-Trust posture breakdown, perimeter containment SLAs, brute-force anomalies, and audit log integrity.",
                "target_audience": "CISO, SecOps Lead & Audit Committee",
                "supported_formats": ["MARKDOWN", "HTML", "JSON"],
            },
            {
                "type": ReportType.DATA_PLATFORM_HEALTH_AUDIT.value,
                "title": "4-Pillar Data Quality & Analytics Platform Scorecard",
                "description": "ETL pipeline health, schema conformance, cohort churn model accuracy, and database p95 latencies.",
                "target_audience": "Chief Data Officer & Principal Engineers",
                "supported_formats": ["MARKDOWN", "HTML", "JSON"],
            },
        ]

    @classmethod
    def generate_report(
        cls,
        report_type: ReportType = ReportType.BOARDROOM_QUARTERLY_BRIEF,
        period: str = "Q1 2026",
        report_format: ReportFormat = ReportFormat.MARKDOWN,
        author: str = "AegisIQ Decision Engine",
    ) -> ExecutiveReportPayload:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_id = f"rep-{int(time.time())}-{report_type.value.lower()[:6]}"

        sections: List[ReportSection] = []
        exec_summary = ""
        report_title = ""

        # 1. BOARDROOM_QUARTERLY_BRIEF
        if report_type == ReportType.BOARDROOM_QUARTERLY_BRIEF:
            report_title = f"AegisIQ Executive Boardroom Briefing — {period}"
            exec_summary = (
                f"During {period}, the enterprise demonstrated resilient financial and operational expansion. "
                "Annual Recurring Revenue (ARR) reached $24.8M (+18.4% YoY), outpacing quarterly budget guidance by 12.7%. "
                "Gross profit margins expanded to 68.4% due to cloud compute rightsizing. "
                "The cybersecurity perimeter maintained a Zero-Trust score of 12/100 (Optimal) with zero critical vulnerabilities open."
            )
            sections = [
                ReportSection(
                    title="Financial Health & Revenue Velocity",
                    order=1,
                    key_metrics={"ARR": "$24.8M", "YoY_Growth": "+18.4%", "Gross_Margin": "68.4%", "NRR": "114.2%"},
                    narrative_summary="Revenue growth was driven by accelerated adoption in Tier-1 enterprise accounts and 32% growth in multi-product add-on attachments.",
                    bullet_points=[
                        "Net Revenue Retention pacing at 114.2% across North America and EMEA.",
                        "Holt-Winters statistical forecasting projects Q1 2027 ARR at $33.2M ($R^2=0.962$).",
                        "Cash flow runway remains fully capitalized across the $4.2M capital budget.",
                    ],
                ),
                ReportSection(
                    title="Cybersecurity Posture & SIEM Threat Defense",
                    order=2,
                    key_metrics={"Zero_Trust_Score": "12/100 (Optimal)", "Open_Criticals": "0", "SIEM_Events_24h": "1,420", "Quarantined_IPs": "48"},
                    narrative_summary="Automated SIEM detection isolated 48 malicious scanning IPs with zero lateral movement detected.",
                    bullet_points=[
                        "ISO 27001:2022 access control controls verified across all tier-1 clusters.",
                        "Zero-Trust risk scorecard remains in the lowest risk decile (12/100).",
                        "FIDO2 hardware key enforcement scheduled for remaining engineering pods.",
                    ],
                ),
                ReportSection(
                    title="Platform Architecture & SLA Reliability",
                    order=3,
                    key_metrics={"SLA_Uptime": "99.99%", "p95_API_Latency": "42ms", "ETL_Data_Quality": "96.8%", "Active_Tenants": "1,840"},
                    narrative_summary="Multi-region container clusters delivered 99.99% availability with zero unscheduled downtime.",
                    bullet_points=[
                        "Automated ETL pipelines processed 12.4M records with 96.8% data quality scorecard.",
                        "API latency percentiles (p95: 42ms, p99: 84ms) meet all contractual enterprise SLAs.",
                    ],
                ),
            ]

        # 2. FINANCIAL_OPERATIONAL_REVIEW
        elif report_type == ReportType.FINANCIAL_OPERATIONAL_REVIEW:
            report_title = f"Executive Financial Performance & Unit Economics — {period}"
            exec_summary = (
                f"Financial operations for {period} achieved record capital efficiency. "
                "Operating cash flow reached $6.8M, supported by a 14-month CAC-to-LTV payback period and 68.4% gross margins."
            )
            sections = [
                ReportSection(
                    title="Revenue & Gross Margin Breakdown",
                    order=1,
                    key_metrics={"ARR": "$24.8M", "EBITDA_Margin": "28.6%", "Gross_Margin": "68.4%", "CAC_Payback": "14 Mos"},
                    narrative_summary="Gross margin expansion of 340 bps YoY was achieved through infrastructure rightsizing and database query optimizations.",
                    bullet_points=[
                        "Recurring subscription revenue represents 94.2% of total platform bookings.",
                        "Average revenue per account expanded by 16.8% across tier-1 cohorts.",
                    ],
                )
            ]

        # 3. CYBERSECURITY_COMPLIANCE_POSTURE
        elif report_type == ReportType.CYBERSECURITY_COMPLIANCE_POSTURE:
            report_title = f"Cybersecurity SIEM & ISO 27001 Compliance Audit — {period}"
            exec_summary = (
                f"Cybersecurity posture for {period} conforms fully with ISO/IEC 27001:2022 and SOC2 Type II requirements. "
                "Zero data leakage or exfiltration attempts breached edge perimeter filters."
            )
            sections = [
                ReportSection(
                    title="SIEM Threat Studio Incident Summary",
                    order=1,
                    key_metrics={"Risk_Score": "12/100", "Total_Events": "14,290", "Quarantined": "48", "Containment_SLA": "<120s"},
                    narrative_summary="Edge quarantine rules automatically isolated 48 malicious IP subnets with zero false positives reported.",
                    bullet_points=[
                        "100% of audit logs cryptographically signed and archived for compliance verification.",
                        "Brute-force SSH and API probe attempts dropped by 44% following automated IP blocking.",
                    ],
                )
            ]

        # 4. DATA_PLATFORM_HEALTH_AUDIT
        else:
            report_title = f"Enterprise Data Platform Quality & Telemetry Audit — {period}"
            exec_summary = (
                f"Data integration pipelines and machine learning forecasting models operated with 96.8% composite data quality scorecards in {period}."
            )
            sections = [
                ReportSection(
                    title="4-Pillar Data Quality Scorecard",
                    order=1,
                    key_metrics={"Completeness": "98.4%", "Uniqueness": "99.1%", "Validity": "95.6%", "Consistency": "94.2%"},
                    narrative_summary="Data pipelines ingested and validated 12.4M records across 4 disparate enterprise database sources.",
                    bullet_points=[
                        "Zero critical schema drift events detected during daily ETL runs.",
                        "Database query latency p95 maintained at 42ms across all active tenants.",
                    ],
                )
            ]

        # Recommendations
        raw_recs = BusinessRecommendationEngine.generate_recommendations(report_type.value, PersonaType.CEO)
        recs_dicts = [r.model_dump() for r in raw_recs]

        # Render Content
        if report_format == ReportFormat.HTML:
            rendered = ReportTemplateRenderer.render_html(
                report_title, period, author, now_str, exec_summary, sections, recs_dicts
            )
        elif report_format == ReportFormat.JSON:
            rendered = f'{{"report_id": "{report_id}", "title": "{report_title}", "status": "COMPILED"}}'
        else:
            rendered = ReportTemplateRenderer.render_markdown(
                report_title, period, author, now_str, exec_summary, sections, recs_dicts
            )

        report = ExecutiveReportPayload(
            report_id=report_id,
            report_type=report_type,
            title=report_title,
            period=period,
            generated_at=now_str,
            author=author,
            executive_summary=exec_summary,
            sections=sections,
            recommendations=recs_dicts,
            rendered_content=rendered,
            format=report_format,
        )

        cls._archive[report_id] = report
        logger.info(f"Generated executive report: {report_id} ({report_type.value}) in {report_format.value}")
        return report

    @classmethod
    def list_history(cls, limit: int = 20) -> List[ExecutiveReportPayload]:
        if not cls._archive:
            # Seed default demo report
            cls.generate_report(ReportType.BOARDROOM_QUARTERLY_BRIEF, "Q1 2026", ReportFormat.MARKDOWN)
        return list(cls._archive.values())[:limit]

    @classmethod
    def get_report(cls, report_id: str) -> ExecutiveReportPayload:
        report = cls._archive.get(report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' not found.")
        return report
