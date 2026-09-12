from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.explainability_service.types import CitationGraph, DecisionAuditRecord


class InspectDecisionRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    persona: Optional[str] = "CEO"


class TransparencyInspectionResponse(BaseModel):
    query: str
    intent_classification: str
    target_collection: str
    retrieved_chunks_count: int
    average_similarity_score: float
    grounding_status: str
    reasoning_steps: List[str] = []
    confidence_calibration: Dict[str, Any] = {}


class CitationGraphRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    collection_name: Optional[str] = "enterprise_knowledge"


class CitationGraphResponse(BaseModel):
    query: str
    graph: CitationGraph


class AuditRecordResponse(BaseModel):
    audit_id: str
    timestamp: str
    user_id: int
    user_email: str
    query: str
    answer_snippet: str
    referenced_doc_ids: List[str] = []
    confidence_score: float
    total_latency_ms: float
    compliance_status: str


class ExplainabilityStatsResponse(BaseModel):
    grounding_pass_rate_percentage: float
    average_decision_confidence: float
    total_audited_decisions: int
    hallucination_incidents_recorded: int
    compliance_standards: List[str] = []
    verification_mode: str
