from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DistanceMetric(str, Enum):
    COSINE = "COSINE"
    EUCLIDEAN = "EUCLIDEAN"
    DOT_PRODUCT = "DOT_PRODUCT"


class VectorStoreType(str, Enum):
    CHROMA_DB = "CHROMA_DB"
    QDRANT = "QDRANT"
    ENTERPRISE_MEMORY = "ENTERPRISE_MEMORY"


class VectorRecord(BaseModel):
    id: str
    vector: List[float]
    document: str
    metadata: Dict[str, Any] = {}


class VectorSearchResult(BaseModel):
    id: str
    document: str
    score: float
    metadata: Dict[str, Any] = {}


class CollectionInfo(BaseModel):
    name: str
    total_vectors: int
    dimensions: int
    distance_metric: DistanceMetric
    created_at: str
    description: Optional[str] = None
