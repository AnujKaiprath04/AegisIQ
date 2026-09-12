from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.embedding_service.types import EmbeddingModelType, ModelMetadata


class EmbeddingGenerateRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="List of text chunks to vectorize")
    model_type: Optional[EmbeddingModelType] = None


class EmbeddingGenerateResponse(BaseModel):
    model_name: str
    dimensions: int
    total_texts_embedded: int
    latency_ms: float
    embeddings: List[List[float]]


class QueryEmbeddingRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Search query string")
    model_type: Optional[EmbeddingModelType] = None


class QueryEmbeddingResponse(BaseModel):
    model_name: str
    dimensions: int
    query: str
    latency_ms: float
    query_embedding: List[float]


class ModelListResponse(BaseModel):
    active_model: str
    models: List[ModelMetadata]


class SwitchModelRequest(BaseModel):
    model_type: EmbeddingModelType


class SwitchModelResponse(BaseModel):
    message: str
    active_model: str
    dimensions: int


class EmbeddingBenchmarkResponse(BaseModel):
    active_model: str
    dimensions: int
    semantic_match_security: float
    semantic_match_finance: float
    cross_domain_similarity_low: float
    benchmark_status: str
