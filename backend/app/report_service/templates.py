from typing import Any, Dict, List
from app.report_service.types import ReportSection


class ReportTemplateRenderer:
    """Renders structured executive reports into Markdown and Executive Dark Theme HTML."""

    @classmethod
    def render_markdown(
        cls,
        title: str,
        period: str,
        author: str,
        generated_at: str,
        executive_summary: str,
        sections: List[ReportSection],
        recommendations: List[Dict[str, Any]],
    ) -> str:
        md_lines = [
            f"# {title}",
            f"**Reporting Period**: {period} | **Author**: {author} | **Generated**: {generated_at}",
            "\n---\n",
            "## 🎯 Executive Summary",
            executive_summary,
            "\n---\n",
        ]

        # Render Sections
        for sec in sorted(sections, key=lambda s: s.order):
            md_lines.append(f"## {sec.order}. {sec.title}")
            
            if sec.key_metrics:
                md_lines.append("\n| Metric | Telemetry Value |")
                md_lines.append("|---|---|")
                for k, v in sec.key_metrics.items():
                    clean_k = k.replace("_", " ").title()
                    md_lines.append(f"| **{clean_k}** | `{v}` |")
                md_lines.append("")

            md_lines.append(sec.narrative_summary)
            md_lines.append("")

            if sec.bullet_points:
                for b in sec.bullet_points:
                    md_lines.append(f"- {b}")
                md_lines.append("")

            md_lines.append("---\n")

        # Render Recommendations
        if recommendations:
            md_lines.append("## 🚀 Prioritized Strategic Recommendations")
            for idx, rec in enumerate(recommendations):
                impact = rec.get("expected_impact_usd", 0)
                effort = rec.get("effort_level", "MEDIUM")
                dept = rec.get("department", "EXECUTIVE")
                md_lines.append(
                    f"### {idx + 1}. {rec.get('title', 'Action')}\n"
                    f"- **Expected Financial ROI**: `${impact:,.2f}`\n"
                    f"- **Implementation Effort**: `{effort}` | **Ownership**: `{dept}`\n"
                    f"- **Description**: {rec.get('description', '')}\n"
                )

        return "\n".join(md_lines)

    @classmethod
    def render_html(
        cls,
        title: str,
        period: str,
        author: str,
        generated_at: str,
        executive_summary: str,
        sections: List[ReportSection],
        recommendations: List[Dict[str, Any]],
    ) -> str:
        sections_html = []
        for sec in sorted(sections, key=lambda s: s.order):
            metrics_badges = "".join(
                f'<div style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.3);padding:10px 16px;border-radius:8px;text-align:center;">'
                f'<div style="font-size:12px;color:#94a3b8;text-transform:uppercase;">{k.replace("_", " ")}</div>'
                f'<div style="font-size:18px;font-weight:700;color:#38bdf8;">{v}</div>'
                f'</div>'
                for k, v in sec.key_metrics.items()
            )

            bullets_html = "".join(f'<li style="margin-bottom:6px;color:#cbd5e1;">{b}</li>' for b in sec.bullet_points)

            sections_html.append(
                f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:24px;margin-bottom:24px;">'
                f'<h2 style="color:#f8fafc;font-size:20px;margin-top:0;border-bottom:1px solid #334155;padding-bottom:10px;">{sec.order}. {sec.title}</h2>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px;">{metrics_badges}</div>'
                f'<p style="color:#cbd5e1;line-height:1.6;font-size:15px;">{sec.narrative_summary}</p>'
                f'<ul style="padding-left:20px;">{bullets_html}</ul>'
                f'</div>'
            )

        recs_html = "".join(
            f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:16px;margin-bottom:12px;">'
            f'<div style="font-weight:700;color:#34d399;font-size:16px;">{idx + 1}. {r.get("title")}</div>'
            f'<div style="font-size:13px;color:#94a3b8;margin:4px 0;">Impact: <strong style="color:#f8fafc">${r.get("expected_impact_usd", 0):,.2f}</strong> | Effort: <strong>{r.get("effort_level")}</strong> | Owner: <strong>{r.get("department")}</strong></div>'
            f'<div style="color:#cbd5e1;font-size:14px;margin-top:6px;">{r.get("description")}</div>'
            f'</div>'
            for idx, r in enumerate(recommendations)
        )

        return (
            f'<!DOCTYPE html>'
            f'<html>'
            f'<head><meta charset="utf-8"><title>{title}</title></head>'
            f'<body style="background:#020617;color:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;padding:32px;max-width:960px;margin:0 auto;line-height:1.5;">'
            f'<div style="border-bottom:2px solid #3b82f6;padding-bottom:16px;margin-bottom:24px;">'
            f'<div style="color:#60a5fa;font-size:14px;font-weight:700;letter-spacing:1px;">AEGISIQ DECISION INTELLIGENCE PLATFORM</div>'
            f'<h1 style="font-size:28px;margin:8px 0;color:#ffffff;">{title}</h1>'
            f'<div style="color:#94a3b8;font-size:13px;">Period: {period} | Prepared by: {author} | Generated: {generated_at}</div>'
            f'</div>'
            f'<div style="background:linear-gradient(135deg,rgba(30,41,59,0.8),rgba(15,23,42,0.9));border:1px solid #334155;border-radius:12px;padding:20px;margin-bottom:24px;">'
            f'<h3 style="margin-top:0;color:#38bdf8;">🎯 Executive Summary</h3>'
            f'<p style="color:#e2e8f0;line-height:1.6;margin-bottom:0;">{executive_summary}</p>'
            f'</div>'
            f'{"".join(sections_html)}'
            f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:24px;margin-top:24px;">'
            f'<h2 style="color:#f8fafc;font-size:20px;margin-top:0;">🚀 Prioritized Strategic Recommendations</h2>'
            f'{recs_html}'
            f'</div>'
            f'</body>'
            f'</html>'
        )
