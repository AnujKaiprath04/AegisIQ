from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.rag_engine import (
    RAGQueryRequestSchema,
    RAGQueryResponseSchema,
    RAGRetrieveRequestSchema,
    RAGRetrieveResponseSchema,
    RAGTelemetryResponseSchema,
)
from app.rag_engine.pipeline import RAGPipeline
from app.rag_engine.query_processor import QueryUnderstandingEngine
from app.rag_engine.types import RAGQueryRequest

router = APIRouter(prefix="/ai/rag", tags=["Part 2 - Module 6: Retrieval-Augmented Generation (RAG)"])


@router.post("/query", response_model=RAGQueryResponseSchema)
def query_rag_pipeline(
    req: RAGQueryRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Execute end-to-end RAG question answering with verified citations and anti-hallucination guardrails."""
    internal_req = RAGQueryRequest(
        query=req.query,
        collection_name=req.collection_name,
        top_k=req.top_k,
        department_filter=req.department_filter,
        provider_type=req.provider_type,
        system_persona=req.system_persona,
    )
    res = RAGPipeline.execute_rag(internal_req)
    return RAGQueryResponseSchema(**res.model_dump())


@router.post("/retrieve", response_model=RAGRetrieveResponseSchema)
def retrieve_rag_context(
    req: RAGRetrieveRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Retrieve, rerank, and compress context passages without LLM generation for retrieval inspection."""
    res = RAGPipeline.retrieve_only(
        query=req.query,
        collection_name=req.collection_name or "enterprise_knowledge",
        top_k=req.top_k or 5,
        department_filter=req.department_filter,
    )
    return RAGRetrieveResponseSchema(**res)


@router.post("/explain-query")
def explain_rag_query(
    req: RAGRetrieveRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Analyze query intent, infer domain/department filters, and generate sub-queries."""
    return QueryUnderstandingEngine.analyze_and_expand(
        query=req.query,
        default_collection=req.collection_name or "enterprise_knowledge",
        override_dept=req.department_filter,
    )


@router.get("/telemetry", response_model=RAGTelemetryResponseSchema)
def get_rag_telemetry(
    current_user: User = Depends(get_current_user),
):
    """Retrieve RAG pipeline latency benchmarks, query throughput, and anti-hallucination status."""
    res = RAGPipeline.get_telemetry()
    return RAGTelemetryResponseSchema(**res)
