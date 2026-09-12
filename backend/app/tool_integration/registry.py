import logging
from typing import Any, Dict, List, Optional
from app.tool_integration.types import ToolDefinition

logger = logging.getLogger("aegisiq.tool_integration.registry")

REGISTERED_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="query_financial_kpis",
        description="Retrieve real-time financial metrics, including ARR, gross profit margin, EBITDA, and CAC-to-LTV payback from the BI telemetry engine.",
        parameters_schema={
            "type": "object",
            "properties": {
                "metric_names": {"type": "array", "items": {"type": "string"}, "description": "List of metric keys e.g. ['ARR', 'GROSS_MARGIN']"},
                "period": {"type": "string", "default": "Q1 2026", "description": "Fiscal quarter or period"},
            },
        },
        required_permissions=["Viewer", "Data Analyst", "Executive", "Admin"],
    ),
    ToolDefinition(
        name="synthesize_sql_query",
        description="Translate a natural language question into a verified, read-only PostgreSQL analytics query with schema catalog injection.",
        parameters_schema={
            "type": "object",
            "properties": {
                "natural_language_question": {"type": "string", "description": "Business query to translate to SQL"},
                "target_schema": {"type": "string", "default": "public", "description": "Database schema"},
            },
            "required": ["natural_language_question"],
        },
        required_permissions=["Data Analyst", "Executive", "Admin"],
    ),
    ToolDefinition(
        name="trigger_quarantine_action",
        description="Trigger the SIEM Threat Studio playbook to quarantine a malicious IP subnet or suspend compromised credentials at the edge firewall.",
        parameters_schema={
            "type": "object",
            "properties": {
                "target_ip": {"type": "string", "description": "IP address or subnet to quarantine"},
                "reason": {"type": "string", "description": "Justification or incident trigger"},
                "isolation_level": {"type": "string", "enum": ["EDGE_FIREWALL", "FULL_CLUSTER"], "default": "EDGE_FIREWALL"},
            },
            "required": ["target_ip", "reason"],
        },
        required_permissions=["Security Auditor", "Admin"],
    ),
    ToolDefinition(
        name="export_executive_report",
        description="Compile and export a cross-domain boardroom report in Markdown or HTML format.",
        parameters_schema={
            "type": "object",
            "properties": {
                "report_type": {"type": "string", "enum": ["BOARDROOM_QUARTERLY_BRIEF", "FINANCIAL_OPERATIONAL_REVIEW", "CYBERSECURITY_COMPLIANCE_POSTURE"], "default": "BOARDROOM_QUARTERLY_BRIEF"},
                "period": {"type": "string", "default": "Q1 2026"},
                "format": {"type": "string", "enum": ["MARKDOWN", "HTML", "JSON"], "default": "MARKDOWN"},
            },
        },
        required_permissions=["Data Analyst", "Executive", "Admin"],
    ),
    ToolDefinition(
        name="fetch_dataset_quality_score",
        description="Fetch 4-pillar data quality scorecards (Completeness, Uniqueness, Validity, Consistency) for registered platform datasets.",
        parameters_schema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "default": "ds-fin-001", "description": "Dataset identifier"},
            },
        },
        required_permissions=["Viewer", "Data Analyst", "Executive", "Admin"],
    ),
]


class EnterpriseToolRegistry:
    """Registry maintaining metadata, schemas, and permissions for all platform business tools."""

    _tools: Dict[str, ToolDefinition] = {t.name: t for t in REGISTERED_TOOLS}

    @classmethod
    def list_tools(cls) -> List[ToolDefinition]:
        return list(cls._tools.values())

    @classmethod
    def get_tool(cls, name: str) -> Optional[ToolDefinition]:
        return cls._tools.get(name.lower().strip())
