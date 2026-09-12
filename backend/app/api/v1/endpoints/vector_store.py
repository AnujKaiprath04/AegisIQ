from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.vector_store import (
    CollectionInfo,
    CreateCollectionRequest,
    VectorSearchRequest,
    VectorSearchResponse,
    VectorStatsResponse,
    VectorUpsertRequest,
    VectorUpsertResponse,
)
from app.vector_service.manager import VectorStoreManager

router = APIRouter(prefix="/ai/vector", tags=["Vector Database"])


@router.get("/collections", response_model=List[CollectionInfo])
def list_vector_collections(
    current_user: User = Depends(get_current_user),
):
    """List all active vector collections, vector counts, and dimensions."""
    return VectorStoreManager.list_collections()


@router.post("/collections", response_model=CollectionInfo, status_code=status.HTTP_201_CREATED)
def create_vector_collection(
    req: CreateCollectionRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Create a new named vector collection / namespace in the vector database."""
    return VectorStoreManager.create_collection(
        name=req.name,
        dimensions=req.dimensions,
        description=req.description,
    )


@router.delete("/collections/{collection_name}")
def delete_vector_collection(
    collection_name: str,
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Delete a vector collection and purge all indexed vectors."""
    deleted = VectorStoreManager.delete_collection(collection_name)
    return {"message": f"Collection '{collection_name}' deleted.", "success": deleted}


@router.post("/upsert", response_model=VectorUpsertResponse)
def upsert_vectors(
    req: VectorUpsertRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Vectorize and upsert document text chunks into the specified collection."""
    res = VectorStoreManager.upsert_chunks(
        collection_name=req.collection_name,
        chunk_texts=req.chunk_texts,
        metadatas=req.metadatas,
    )
    return VectorUpsertResponse(**res)


@router.post("/search", response_model=VectorSearchResponse)
def search_vectors(
    req: VectorSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute top-k nearest neighbor vector similarity search with metadata filtering."""
    res = VectorStoreManager.similarity_search(
        query=req.query,
        collection_name=req.collection_name,
        top_k=req.top_k,
        where_filter=req.where_filter,
    )
    return VectorSearchResponse(**res)


@router.get("/stats", response_model=VectorStatsResponse)
def get_vector_store_stats(
    current_user: User = Depends(get_current_user),
):
    """Retrieve global vector database metrics, memory footprint, and collection statistics."""
    res = VectorStoreManager.get_stats()
    return VectorStatsResponse(**res)
