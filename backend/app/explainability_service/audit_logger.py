import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.explainability_service.types import DecisionAuditRecord
from app.rag_engine.types import RAGCitation

logger = logging.getLogger("aegisiq.explainability.audit")


class AIAuditLogger:
    """Maintains an immutable compliance audit trail for AI inference and source attribution."""

    _audit_logs: List[DecisionAuditRecord] = []

    @classmethod
    def initialize_defaults(cls):
        if not cls._audit_logs:
            now = datetime.now(timezone.utc).isoformat()
            cls._audit_logs.append(
                DecisionAuditRecord(
                    audit_id="audit-seed-01",
                    timestamp=now,
                    user_id=1,
                    user_email="admin@aegisiq.com",
                    query="What are our mandatory ISO 27001 access control protocols?",
                    answer_snippet="Access control mandates hardware MFA keys for all tier-1 engineering systems...",
                    referenced_doc_ids=["doc-sec-iso27001"],
                    confidence_score=0.942,
                    total_latency_ms=28.4,
                    compliance_status="VERIFIED_GROUNDED",
                )
            )
            cls._audit_logs.append(
                DecisionAuditRecord(
                    audit_id="audit-seed-02",
                    timestamp=now,
                    user_id=2,
                    user_email="executive@aegisiq.com",
                    query="Summarize our Q1 ARR and gross margin trajectory.",
                    answer_snippet="ARR is pacing at $24.8M with a 68.4% gross profit margin...",
                    referenced_doc_ids=["doc-fin-q1-2026"],
                    confidence_score=0.968,
                    total_latency_ms=31.2,
                    compliance_status="VERIFIED_GROUNDED",
                )
            )

    @classmethod
    def log_decision(
        cls,
        user_id: int,
        user_email: str,
        query: str,
        answer: str,
        citations: List[RAGCitation],
        confidence_score: float,
        total_latency_ms: float,
    ) -> DecisionAuditRecord:
        cls.initialize_defaults()
        audit_id = f"audit-{int(time.time())}-{len(cls._audit_logs) + 1}"
        doc_ids = [c.document_title for c in citations]

        record = DecisionAuditRecord(
            audit_id=audit_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            user_email=user_email,
            query=query,
            answer_snippet=answer[:180] + ("..." if len(answer) > 180 else ""),
            referenced_doc_ids=doc_ids,
            confidence_score=round(confidence_score, 4),
            total_latency_ms=round(total_latency_ms, 2),
            compliance_status="VERIFIED_GROUNDED" if confidence_score >= 0.70 else "LOW_CONFIDENCE_REVIEW",
        )
        cls._audit_logs.insert(0, record)
        logger.info(f"Recorded AI decision audit record: {audit_id}")
        return record

    @classmethod
    def list_logs(cls, limit: int = 50, user_id: Optional[int] = None) -> List[DecisionAuditRecord]:
        cls.initialize_defaults()
        records = cls._audit_logs
        if user_id:
            records = [r for r in records if r.user_id == user_id]
        return records[:limit]
