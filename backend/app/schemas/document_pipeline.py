from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChunkItemResponse(BaseModel):
    chunk_index: int
    content: str
    token_count: int
    char_length: int
    char_start: int
    char_end: int
    section_header: Optional[str] = None


class DirectParseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="Raw text snippet to clean and chunk")
    chunk_size: Optional[int] = Field(default=500, ge=100, le=4000)
    chunk_overlap: Optional[int] = Field(default=80, ge=0, le=1000)


class DirectParseResponse(BaseModel):
    total_chunks: int
    total_tokens: int
    latency_ms: float
    chunks: List[ChunkItemResponse]


class PipelineProcessResponse(BaseModel):
    document_id: int
    title: str
    file_format: str
    status: str
    total_chunks_created: int
    total_tokens_estimated: int
    processing_latency_ms: float
    chunks: List[ChunkItemResponse] = []


class PipelineStatusResponse(BaseModel):
    document_id: int
    title: str
    status: str
    last_indexed_at: Optional[datetime] = None
    estimated_chunks: int
