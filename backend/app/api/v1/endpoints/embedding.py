from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.embedding import (
    EmbeddingBenchmarkResponse,
    EmbeddingGenerateRequest,
    EmbeddingGenerateResponse,
    ModelListResponse,
    QueryEmbeddingRequest,
    QueryEmbeddingResponse,
    SwitchModelRequest,
    SwitchModelResponse,
)
from app.embedding_service.engine import EmbeddingEngine
from app.embedding_service.registry import EmbeddingModelRegistry

router = APIRouter(prefix="/ai/embedding", tags=["Part 2 - Module 4: Embedding Engine"])


@router.post("/generate", response_model=EmbeddingGenerateResponse)
def generate_embeddings(
    req: EmbeddingGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate dense, L2-normalized vector embeddings for a list of document passages."""
    res = EmbeddingEngine.generate_embeddings(texts=req.texts, model_type=req.model_type)
    return EmbeddingGenerateResponse(**res)


@router.post("/query", response_model=QueryEmbeddingResponse)
def generate_query_embedding(
    req: QueryEmbeddingRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate normalized query embedding with model-specific asymmetric prefixing."""
    res = EmbeddingEngine.generate_query_embedding(query=req.query, model_type=req.model_type)
    return QueryEmbeddingResponse(**res)


@router.get("/models", response_model=ModelListResponse)
def list_embedding_models(
    current_user: User = Depends(get_current_user),
):
    """List registered embedding models, dimensions, context limits, and active status."""
    models = EmbeddingModelRegistry.list_models()
    return ModelListResponse(
        active_model=EmbeddingModelRegistry.get_active_model().model_name,
        models=models,
    )


@router.post("/switch-model", response_model=SwitchModelResponse)
def switch_active_embedding_model(
    req: SwitchModelRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Dynamically switch the platform default active embedding model in the registry."""
    new_model = EmbeddingModelRegistry.switch_model(req.model_type)
    return SwitchModelResponse(
        message=f"Active embedding model successfully switched to {new_model.model_name}.",
        active_model=new_model.model_name,
        dimensions=new_model.dimensions,
    )


@router.get("/benchmark", response_model=EmbeddingBenchmarkResponse)
def run_embedding_benchmark(
    current_user: User = Depends(get_current_user),
):
    """Execute cosine similarity separation benchmark across cross-domain enterprise statements."""
    res = EmbeddingEngine.run_similarity_benchmark()
    return EmbeddingBenchmarkResponse(**res)
