import re
from typing import Tuple
from app.ai_gateway.types import QueryIntent


class IntentClassifier:
    @staticmethod
    def classify(prompt: str) -> Tuple[QueryIntent, float, str]:
        """Classify user prompt into structured enterprise intent with confidence score."""
        p = prompt.lower().strip()

        # 1. Executive Report Generation
        if any(k in p for k in ["report", "brief", "boardroom", "summary", "pdf"]):
            return (
                QueryIntent.EXECUTIVE_REPORT,
                0.96,
                "Prompt requests formal multi-section executive reporting synthesis.",
            )


        # 2. Enterprise RAG Document Query
        if any(k in p for k in ["document", "policy", "handbook", "iso", "soc2", "clause", "sla", "contract", "section", "compliance"]):
            return (
                QueryIntent.ENTERPRISE_RAG,
                0.94,
                "Prompt requires semantic vector retrieval from unstructured enterprise documents.",
            )

        # 3. Structured Business Analytics / KPIs
        if any(k in p for k in ["kpi", "margin", "revenue", "arr", "sales", "cac", "churn", "ebitda", "variance", "growth", "why are sales", "financials"]):
            return (
                QueryIntent.BUSINESS_ANALYTICS,
                0.95,
                "Prompt targets structured financial and operational performance metrics.",
            )

        # 4. SQL Analytics Synthesis
        if any(k in p for k in ["sql", "query database", "table", "schema", "count rows", "select", "join"]):
            return (
                QueryIntent.SQL_SYNTHESIS,
                0.91,
                "Prompt requests natural language translation to relational SQL query.",
            )

        # 5. Default Conversational QA
        return (
            QueryIntent.CONVERSATIONAL_QA,
            0.88,
            "General enterprise conversational Q&A and decision support.",
        )
