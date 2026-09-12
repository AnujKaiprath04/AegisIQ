from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EmbeddingModelType(str, Enum):
    BGE_SMALL = "BGE_SMALL"
    MINILM_L6 = "MINILM_L6"
    E5_SMALL = "E5_SMALL"
    LOCAL_ENTERPRISE = "LOCAL_ENTERPRISE"


class PoolingStrategy(str, Enum):
    MEAN = "MEAN"
    CLS = "CLS"


class ModelMetadata(BaseModel):
    model_type: EmbeddingModelType
    model_name: str
    dimensions: int
    max_seq_length: int
    pooling_strategy: PoolingStrategy
    is_active: bool
    latency_ms: float
    description: str
