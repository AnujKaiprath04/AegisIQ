from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.vector_service.types import CollectionInfo, VectorSearchResult


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    dimensions: int = Field(default=384, ge=32, le=4096)
    description: Optional[str] = None


class VectorUpsertRequest(BaseModel):
    collection_name: str = Field(default="enterprise_knowledge")
    chunk_texts: List[str] = Field(..., min_length=1)
    metadatas: Optional[List[Dict[str, Any]]] = None


class VectorUpsertResponse(BaseModel):
    collection_name: str
    upserted_count: int
    latency_ms: float
    total_collection_vectors: int


class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    collection_name: str = Field(default="enterprise_knowledge")
    top_k: int = Field(default=5, ge=1, le=50)
    where_filter: Optional[Dict[str, Any]] = None


class VectorSearchResponse(BaseModel):
    query: str
    collection_name: str
    top_k: int
    where_filter: Optional[Dict[str, Any]] = None
    latency_ms: float
    total_matches: int
    results: List[VectorSearchResult] = []


class VectorStatsResponse(BaseModel):
    store_type: str
    active_collections_count: int
    total_vectors_indexed: int
    estimated_memory_kb: float
    collections: List[CollectionInfo] = []
