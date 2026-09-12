from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    QUERY = "QUERY"
    CLAIM = "CLAIM"
    PASSAGE = "PASSAGE"
    DOCUMENT = "DOCUMENT"


class CitationNode(BaseModel):
    id: str
    label: str
    node_type: NodeType
    metadata: Dict[str, Any] = {}


class CitationEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str
    weight: float = Field(..., ge=0.0, le=1.0)


class CitationGraph(BaseModel):
    nodes: List[CitationNode] = []
    edges: List[CitationEdge] = []
    total_nodes: int = 0
    total_edges: int = 0


class DecisionAuditRecord(BaseModel):
    audit_id: str
    timestamp: str
    user_id: int
    user_email: str
    query: str
    answer_snippet: str
    referenced_doc_ids: List[str] = []
    confidence_score: float
    total_latency_ms: float
    compliance_status: str = "VERIFIED_GROUNDED"


class TransparencyInspectionResult(BaseModel):
    query: str
    intent_classification: str
    target_collection: str
    retrieved_chunks_count: int
    average_similarity_score: float
    grounding_status: str
    reasoning_steps: List[str] = []
    confidence_calibration: Dict[str, Any] = {}
