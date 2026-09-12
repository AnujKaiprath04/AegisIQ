import logging
from typing import Dict, List, Optional
from app.embedding_service.types import EmbeddingModelType, ModelMetadata, PoolingStrategy
from app.embedding_service.models import (
    BaseEmbeddingModel,
    BGEEmbeddingModel,
    E5EmbeddingModel,
    LocalEnterpriseEmbeddingModel,
    SentenceTransformerModel,
)

logger = logging.getLogger("aegisiq.embedding_service.registry")


class EmbeddingModelRegistry:
    """Registry maintaining active embedding vectorizer models and runtime switches."""

    _models: Dict[EmbeddingModelType, BaseEmbeddingModel] = {
        EmbeddingModelType.BGE_SMALL: BGEEmbeddingModel(),
        EmbeddingModelType.MINILM_L6: SentenceTransformerModel(),
        EmbeddingModelType.E5_SMALL: E5EmbeddingModel(),
        EmbeddingModelType.LOCAL_ENTERPRISE: LocalEnterpriseEmbeddingModel(),
    }

    _active_model_type: EmbeddingModelType = EmbeddingModelType.BGE_SMALL

    @classmethod
    def get_active_model(cls) -> BaseEmbeddingModel:
        return cls._models[cls._active_model_type]

    @classmethod
    def get_active_model_type(cls) -> EmbeddingModelType:
        return cls._active_model_type

    @classmethod
    def switch_model(cls, model_type: EmbeddingModelType) -> BaseEmbeddingModel:
        if model_type not in cls._models:
            raise ValueError(f"Unknown embedding model type: {model_type}")
        cls._active_model_type = model_type
        logger.info(f"Switched active embedding model to: {model_type.value}")
        return cls.get_active_model()

    @classmethod
    def list_models(cls) -> List[ModelMetadata]:
        return [
            ModelMetadata(
                model_type=EmbeddingModelType.BGE_SMALL,
                model_name="BAAI/bge-small-en-v1.5",
                dimensions=384,
                max_seq_length=512,
                pooling_strategy=PoolingStrategy.CLS,
                is_active=(cls._active_model_type == EmbeddingModelType.BGE_SMALL),
                latency_ms=8.4,
                description="Top-performing retrieval embedding model for enterprise document RAG.",
            ),
            ModelMetadata(
                model_type=EmbeddingModelType.MINILM_L6,
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                dimensions=384,
                max_seq_length=256,
                pooling_strategy=PoolingStrategy.MEAN,
                is_active=(cls._active_model_type == EmbeddingModelType.MINILM_L6),
                latency_ms=4.8,
                description="Ultra-fast, lightweight 384-D sentence embedding model.",
            ),
            ModelMetadata(
                model_type=EmbeddingModelType.E5_SMALL,
                model_name="intfloat/e5-small-v2",
                dimensions=384,
                max_seq_length=512,
                pooling_strategy=PoolingStrategy.MEAN,
                is_active=(cls._active_model_type == EmbeddingModelType.E5_SMALL),
                latency_ms=9.1,
                description="Asymmetric text embeddings with passage/query prefixing.",
            ),
            ModelMetadata(
                model_type=EmbeddingModelType.LOCAL_ENTERPRISE,
                model_name="aegisiq-dense-bge-384",
                dimensions=384,
                max_seq_length=512,
                pooling_strategy=PoolingStrategy.MEAN,
                is_active=(cls._active_model_type == EmbeddingModelType.LOCAL_ENTERPRISE),
                latency_ms=1.2,
                description="Zero-dependency air-gapped deterministic vectorizer with L2 normalization.",
            ),
        ]
