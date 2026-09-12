from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.explainability import (
    AuditRecordResponse,
    CitationGraphRequest,
    CitationGraphResponse,
    ExplainabilityStatsResponse,
    InspectDecisionRequest,
    TransparencyInspectionResponse,
)
from app.explainability_service.engine import ExplainabilityEngine
from app.explainability_service.citation_graph import CitationGraphBuilder
from app.explainability_service.audit_logger import AIAuditLogger
from app.rag_engine.pipeline import RAGPipeline
from app.rag_engine.types import RAGQueryRequest

router = APIRouter(prefix="/ai/explainability", tags=["Part 2 - Module 10: Citation & Explainability"])


@router.post("/inspect", response_model=TransparencyInspectionResponse)
def inspect_decision_trajectory(
    req: InspectDecisionRequest,
    current_user: User = Depends(get_current_user),
):
    """Inspect full multi-stage decision trajectory, token metrics, and confidence calibration."""
    res = ExplainabilityEngine.inspect_decision(query=req.query, persona=req.persona or "CEO")
    return TransparencyInspectionResponse(**res.model_dump())


@router.post("/citation-graph", response_model=CitationGraphResponse)
def generate_citation_graph(
    req: CitationGraphRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate an interactive Citation Graph DAG connecting Query, Claims, Passages, and Documents."""
    rag_req = RAGQueryRequest(query=req.query, collection_name=req.collection_name)
    rag_res = RAGPipeline.execute_rag(rag_req)

    # Log to audit store
    AIAuditLogger.log_decision(
        user_id=current_user.id,
        user_email=current_user.email,
        query=req.query,
        answer=rag_res.answer,
        citations=rag_res.citations,
        confidence_score=rag_res.confidence_score,
        total_latency_ms=rag_res.total_latency_ms,
    )

    graph = CitationGraphBuilder.build_graph(
        query=req.query,
        answer=rag_res.answer,
        citations=rag_res.citations,
    )
    return CitationGraphResponse(query=req.query, graph=graph)


@router.get("/audit-logs", response_model=List[AuditRecordResponse])
def get_ai_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Security Auditor"])),
):
    """Retrieve immutable AI decision compliance audit logs for regulatory oversight."""
    logs = AIAuditLogger.list_logs(limit=limit)
    return [AuditRecordResponse(**l.model_dump()) for l in logs]


@router.get("/stats", response_model=ExplainabilityStatsResponse)
def get_explainability_stats(
    current_user: User = Depends(get_current_user),
):
    """Retrieve enterprise explainability metrics (grounding pass rate, avg confidence, standards)."""
    stats = ExplainabilityEngine.get_explainability_stats()
    return ExplainabilityStatsResponse(**stats)
