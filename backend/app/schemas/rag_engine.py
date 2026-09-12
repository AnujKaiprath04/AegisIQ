from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai_gateway.types import LLMProviderType


class RAGCitationSchema(BaseModel):
    source_id: int
    document_title: str
    section: str
    department: str
    relevance_score: float
    snippet: str


class RAGQueryRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Business question for RAG")
    collection_name: Optional[str] = "enterprise_knowledge"
    top_k: Optional[int] = 5
    department_filter: Optional[str] = None
    provider_type: Optional[LLMProviderType] = LLMProviderType.LOCAL_ENTERPRISE
    system_persona: Optional[str] = "CEO"


class RAGQueryResponseSchema(BaseModel):
    query: str
    answer: str
    confidence_score: float
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    retrieved_passages_count: int
    citations: List[RAGCitationSchema] = []


class RAGRetrieveRequestSchema(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    collection_name: Optional[str] = "enterprise_knowledge"
    top_k: Optional[int] = 5
    department_filter: Optional[str] = None


class RAGRetrieveResponseSchema(BaseModel):
    query: str
    analysis: Dict[str, Any]
    latency_ms: float
    passages_count: int
    passages: List[Dict[str, Any]] = []
    citations: List[RAGCitationSchema] = []


class RAGTelemetryResponseSchema(BaseModel):
    pipeline_status: str
    average_retrieval_latency_ms: float
    average_generation_latency_ms: float
    average_total_latency_ms: float
    average_confidence_score: float
    total_queries_served: int
    anti_hallucination_guardrails: str
