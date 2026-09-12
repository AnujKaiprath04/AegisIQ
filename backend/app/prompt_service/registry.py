import logging
from typing import Any, Dict, List, Optional
from app.prompt_service.types import FewShotExample, PromptCategory, PromptTemplate
from app.prompt_service.formatter import PromptFormatter

logger = logging.getLogger("aegisiq.prompt_service.registry")

SEEDED_PROMPT_TEMPLATES: List[PromptTemplate] = [
    PromptTemplate(
        id="prompt-sys-01",
        name="SYSTEM_CORE_COPILOT",
        category=PromptCategory.SYSTEM,
        version="v2.1",
        template_text=(
            "You are the AegisIQ Enterprise AI Decision Copilot operating in {{persona}} mode.\n"
            "Organization Context: {{company_name}} ($24.8M ARR, 68.4% Gross Margin, 99.99% SLA Uptime).\n"
            "Adhere strictly to verified enterprise evidence. Include inline citations for every factual claim."
        ),
        input_variables=["persona", "company_name"],
        description="Master enterprise system prompt with organizational context and anti-hallucination boundaries.",
    ),
    PromptTemplate(
        id="prompt-biz-01",
        name="BUSINESS_KPI_ANALYZER",
        category=PromptCategory.BUSINESS,
        version="v1.4",
        template_text=(
            "Analyze the performance of {{kpi_name}}.\n"
            "Current Telemetry: {{current_value}} | Operational Target: {{target_value}} | Variance: {{variance}}.\n"
            "Context Passages:\n{{context_passages}}\n\n"
            "Please provide:\n"
            "1. Executive Root-Cause Summary\n"
            "2. Primary Performance Drivers\n"
            "3. Actionable Strategic Remedies"
        ),
        input_variables=["kpi_name", "current_value", "target_value", "variance", "context_passages"],
        description="Template for drilling down into KPI variance root-causes and driver attribution.",
    ),
    PromptTemplate(
        id="prompt-rep-01",
        name="EXECUTIVE_BOARDROOM_REPORT",
        category=PromptCategory.REPORT,
        version="v2.0",
        template_text=(
            "# AegisIQ Executive Boardroom Briefing: {{period}}\n\n"
            "Synthesize an executive briefing for the Board of Directors covering:\n"
            "- Financial Health & ARR Trajectory (Pacing: {{arr}}, Target: {{arr_target}})\n"
            "- Gross Margin & Unit Economics (Current: {{margin}})\n"
            "- Operational SLA Uptime & Risk Posture (Zero-Trust Score: {{zero_trust_score}}/100)\n"
            "- Strategic Action Items for {{next_quarter}}"
        ),
        input_variables=["period", "arr", "arr_target", "margin", "zero_trust_score", "next_quarter"],
        description="Standardized multi-pillar executive quarterly boardroom briefing generator.",
    ),
    PromptTemplate(
        id="prompt-sum-01",
        name="DOCUMENT_EXECUTIVE_SUMMARY",
        category=PromptCategory.SUMMARY,
        version="v1.2",
        template_text=(
            "Review the document '{{document_title}}' (Department: {{department}}):\n\n"
            "Document Content:\n{{document_text}}\n\n"
            "Extract:\n"
            "1. Core Purpose & Policy Scope\n"
            "2. Top 3 Critical Compliance Obligations\n"
            "3. Enforcement Mechanisms & Penalty Clauses"
        ),
        input_variables=["document_title", "department", "document_text"],
        description="Extracts executive takeaways, risks, and compliance clauses from raw documents.",
    ),
    PromptTemplate(
        id="prompt-rec-01",
        name="ACTION_RECOMMENDATION_BUILDER",
        category=PromptCategory.RECOMMENDATION,
        version="v1.0",
        template_text=(
            "Based on the following enterprise challenge:\n"
            "'{{challenge_description}}'\n\n"
            "Formulate a structured action recommendation card including:\n"
            "- Action Title & Strategic Intent\n"
            "- Expected Financial Impact (in USD ROI or cost reduction)\n"
            "- Implementation Effort (LOW / MEDIUM / HIGH)\n"
            "- Time Horizon (30 Days / 90 Days / 1 Year)\n"
            "- Owner Department (Executive / Finance / Security / Engineering)"
        ),
        input_variables=["challenge_description"],
        description="Generates prioritized business action cards with financial ROI and effort estimation.",
    ),
    PromptTemplate(
        id="prompt-sql-01",
        name="NL_TO_SQL_SYNTHESIZER",
        category=PromptCategory.SQL,
        version="v2.0",
        template_text=(
            "Translate the natural language question into a clean, read-only PostgreSQL query.\n"
            "Database Schema Catalog:\n{{schema_catalog}}\n\n"
            "User Question: {{user_question}}\n\n"
            "Rules:\n"
            "- Use ONLY SELECT statements (no INSERT/UPDATE/DELETE/DROP).\n"
            "- Enforce tenant boundaries and role filters."
        ),
        input_variables=["schema_catalog", "user_question"],
        few_shot_examples=[
            FewShotExample(
                user_input="Find all enterprise accounts with churn probability > 70%",
                ideal_output="SELECT account_name, churn_risk_score, arr_impact FROM customer_churn_predictions WHERE churn_risk_score > 0.70 ORDER BY arr_impact DESC;",
            )
        ],
        description="Translates natural language questions to validated PostgreSQL analytics queries.",
    ),
    PromptTemplate(
        id="prompt-cot-01",
        name="CHAIN_OF_THOUGHT_REASONING",
        category=PromptCategory.REASONING,
        version="v1.1",
        template_text=(
            "You are evaluating a complex decision scenario: '{{scenario_title}}'.\n\n"
            "Reason through this step-by-step:\n"
            "Step 1: Identify key stakeholders and baseline metrics.\n"
            "Step 2: Evaluate trade-offs between speed, cost, and security compliance.\n"
            "Step 3: Synthesize a definitive recommended course of action."
        ),
        input_variables=["scenario_title"],
        description="Enforces structured chain-of-thought diagnostic reasoning.",
    ),
    PromptTemplate(
        id="prompt-sec-01",
        name="CYBERSECURITY_THREAT_BRIEF",
        category=PromptCategory.SECURITY,
        version="v1.3",
        template_text=(
            "Cybersecurity Incident Brief:\n"
            "Incident Type: {{incident_type}} | Severity: {{severity}} | Target Subnet: {{target_subnet}}\n"
            "Containment Action Taken: {{containment_action}}\n\n"
            "Provide:\n"
            "1. Impact Assessment & Blast Radius Analysis\n"
            "2. Forensic Audit Log Verification (SOC2 / ISO 27001)\n"
            "3. Long-term Hardening Recommendations"
        ),
        input_variables=["incident_type", "severity", "target_subnet", "containment_action"],
        description="Generates cybersecurity threat briefs and containment action summaries.",
    ),
]


class PromptRegistry:
    """Enterprise Prompt Registry maintaining versioned templates and variable rendering."""

    _templates: Dict[str, PromptTemplate] = {}

    @classmethod
    def initialize_registry(cls):
        if not cls._templates:
            for t in SEEDED_PROMPT_TEMPLATES:
                cls._templates[t.name] = t
            logger.info("Initialized PromptRegistry with 8 standard enterprise templates.")

    @classmethod
    def list_templates(cls, category: Optional[PromptCategory] = None) -> List[PromptTemplate]:
        cls.initialize_registry()
        templates = list(cls._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    @classmethod
    def get_template(cls, name: str) -> Optional[PromptTemplate]:
        cls.initialize_registry()
        return cls._templates.get(name.upper())

    @classmethod
    def register_template(cls, template: PromptTemplate) -> PromptTemplate:
        cls.initialize_registry()
        cls._templates[template.name.upper()] = template
        logger.info(f"Registered prompt template: {template.name} ({template.version})")
        return template

    @classmethod
    def render_template(cls, name: str, variables: Dict[str, Any], include_few_shots: bool = True) -> str:
        cls.initialize_registry()
        tpl = cls.get_template(name)
        if not tpl:
            raise ValueError(f"Prompt template '{name}' not found in registry.")

        rendered = PromptFormatter.interpolate(tpl.template_text, variables)
        if include_few_shots and tpl.few_shot_examples:
            rendered = PromptFormatter.attach_few_shots(rendered, tpl.few_shot_examples)

        return rendered
