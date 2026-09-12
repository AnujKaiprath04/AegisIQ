import re
from typing import Any, Dict, List, Optional, Tuple


class QueryUnderstandingEngine:
    """Extracts intent, infers optimal vector collection filters, and generates sub-queries."""

    @classmethod
    def analyze_and_expand(
        cls,
        query: str,
        default_collection: str = "enterprise_knowledge",
        override_dept: Optional[str] = None,
    ) -> Dict[str, Any]:
        q_lower = query.lower().strip()

        inferred_dept = override_dept
        target_collection = default_collection
        intent_type = "GENERAL_ENTERPRISE"
        sub_queries = [query]

        # 1. Infer Domain & Target Collection
        if any(k in q_lower for k in ["security", "iso", "access", "auth", "threat", "firewall", "quarantine"]):
            inferred_dept = inferred_dept or "SECURITY"
            target_collection = "security_policies" if default_collection == "enterprise_knowledge" else default_collection
            intent_type = "CYBERSECURITY_GOVERNANCE"
            sub_queries.append(f"ISO 27001 policy access control requirements: {query}")
        elif any(k in q_lower for k in ["revenue", "arr", "margin", "finance", "ebitda", "sales", "cac", "churn", "growth"]):
            inferred_dept = inferred_dept or "FINANCE"
            target_collection = "financial_reports" if default_collection == "enterprise_knowledge" else default_collection
            intent_type = "FINANCIAL_INTELLIGENCE"
            sub_queries.append(f"Q1 financial performance revenue ARR trajectory: {query}")
        elif any(k in q_lower for k in ["sla", "uptime", "legal", "contract", "agreement", "incident response"]):
            inferred_dept = inferred_dept or "LEGAL"
            target_collection = "legal_slas" if default_collection == "enterprise_knowledge" else default_collection
            intent_type = "LEGAL_SLA_COMPLIANCE"
            sub_queries.append(f"Master SLA uptime commitments severity response: {query}")
        elif any(k in q_lower for k in ["devops", "cloud", "disaster", "failover", "recovery", "kubernetes"]):
            inferred_dept = inferred_dept or "ENGINEERING"
            intent_type = "ENGINEERING_RUNBOOK"
            sub_queries.append(f"Cloud infrastructure disaster recovery failover: {query}")

        where_filter = {"department": inferred_dept.upper()} if inferred_dept and inferred_dept != "ALL" else None

        return {
            "original_query": query,
            "intent_type": intent_type,
            "target_collection": target_collection,
            "inferred_department": inferred_dept,
            "where_filter": where_filter,
            "sub_queries": list(dict.fromkeys(sub_queries)),  # Deduplicate
        }
