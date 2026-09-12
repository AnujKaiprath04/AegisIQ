from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: int
    page_number: int
    section_heading: Optional[str] = None
    embedding_preview: List[float] = []
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentSummary(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    file_size_bytes: int
    total_chunks: int
    total_tokens: int
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentDetail(KnowledgeDocumentSummary):
    chunks: List[DocumentChunkResponse] = []


class MatchedChunkCitation(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    category: str
    page_number: int
    section_heading: Optional[str] = None
    similarity_score: float
    snippet: str


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1500, description="Natural language semantic search or question")
    top_k: int = Field(3, ge=1, le=10, description="Number of top relevant chunks to retrieve")
    category_filter: Optional[str] = Field(None, description="Optional category filter: POLICY, FINANCIAL_FILING, SLA_CONTRACT, SECURITY_COMPLIANCE")


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    matched_citations: List[MatchedChunkCitation] = []
    top_similarity_score: float
    latency_ms: float
    created_at: datetime
