from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.document_pipeline import (
    DirectParseRequest,
    DirectParseResponse,
    PipelineProcessResponse,
    PipelineStatusResponse,
)
from app.document_service.pipeline import DocumentProcessingPipeline
from app.document_service.repository import DocumentRepository

router = APIRouter(prefix="/ai/pipeline", tags=["Part 2 - Module 3: Document Processing Pipeline"])


@router.post("/process/{document_id}", response_model=PipelineProcessResponse)
def process_document_pipeline(
    document_id: int,
    chunk_size: int = Query(500, ge=100, le=4000, description="Target character size per chunk"),
    chunk_overlap: int = Query(80, ge=0, le=1000, description="Character overlap between consecutive chunks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Execute multi-format parsing, text sanitization, and recursive semantic chunking on a document."""
    res = DocumentProcessingPipeline.process_document(
        db=db,
        document_id=document_id,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return PipelineProcessResponse(**res)


@router.post("/parse-text", response_model=DirectParseResponse)
def parse_and_chunk_snippet(
    req: DirectParseRequest,
    current_user: User = Depends(get_current_user),
):
    """Clean and chunk raw text snippet with configurable chunk size and token overlap."""
    res = DocumentProcessingPipeline.parse_and_chunk_direct(
        text=req.text,
        chunk_size=req.chunk_size or 500,
        chunk_overlap=req.chunk_overlap or 80,
    )
    return DirectParseResponse(**res)


@router.get("/status/{document_id}", response_model=PipelineStatusResponse)
def get_document_pipeline_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve document ingestion and indexing status with estimated chunk density."""
    doc = DocumentRepository.get_document_by_id(db=db, document_id=document_id)
    return PipelineStatusResponse(
        document_id=doc.id,
        title=doc.title,
        status=doc.status,
        last_indexed_at=doc.last_indexed_at,
        estimated_chunks=max(3, doc.file_size_bytes // 500000) if doc.file_size_bytes else 4,
    )
