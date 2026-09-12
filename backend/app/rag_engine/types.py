from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai_gateway.types import LLMProviderType


class RAGCitation(BaseModel):
    source_id: int
    document_title: str
    section: str
    department: str
    relevance_score: float
    snippet: str


class CompressedPassage(BaseModel):
    passage_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = {}


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Business question to answer using RAG")
    collection_name: Optional[str] = Field(default="enterprise_knowledge")
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    department_filter: Optional[str] = None
    provider_type: Optional[LLMProviderType] = LLMProviderType.LOCAL_ENTERPRISE
    system_persona: Optional[str] = "CEO"


class RAGResponsePayload(BaseModel):
    query: str
    answer: str
    confidence_score: float
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    retrieved_passages_count: int
    citations: List[RAGCitation] = []
