from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.knowledge_base import (
    KnowledgeDocCreate,
    KnowledgeDocDetail,
    KnowledgeDocSummary,
    KnowledgeDocUpdate,
    KnowledgeStatsResponse,
)
from app.document_service.repository import DocumentRepository

router = APIRouter(prefix="/ai/knowledge", tags=["Part 2 - Module 2: Enterprise Knowledge Base"])


@router.get("/documents", response_model=List[KnowledgeDocSummary])
def list_knowledge_documents(
    department: Optional[str] = Query("ALL", description="Filter by department: FINANCE, SECURITY, LEGAL, ENGINEERING, EXECUTIVE, HR, SALES, ALL"),
    category: Optional[str] = Query("ALL", description="Filter by category: POLICY_GOVERNANCE, FINANCIAL_FILING, OPERATIONAL_RUNBOOK, TECHNICAL_SPEC, CONTRACT_SLA, ALL"),
    file_format: Optional[str] = Query("ALL", description="Filter by format: PDF, DOCX, PPTX, TXT, MARKDOWN, CSV, ALL"),
    tag: Optional[str] = Query(None, description="Filter by specific tag keyword"),
    search: Optional[str] = Query(None, description="Full-text search in title or summary"),
    status_filter: Optional[str] = Query("ALL", description="Filter by status: INDEXED, DRAFT, PROCESSING, ARCHIVED, ALL"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve indexed enterprise knowledge repository documents with multi-attribute filtering."""
    return DocumentRepository.get_documents(
        db=db,
        department=department,
        category=category,
        file_format=file_format,
        search_query=search,
        tag=tag,
        status_filter=status_filter,
    )


@router.get("/documents/{document_id}", response_model=KnowledgeDocDetail)
def get_knowledge_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full metadata, SHA-256 hash, and version details for a single knowledge asset."""
    return DocumentRepository.get_document_by_id(db=db, document_id=document_id)


@router.post("/documents", response_model=KnowledgeDocDetail, status_code=status.HTTP_201_CREATED)
def create_knowledge_document(
    req: KnowledgeDocCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Register a new enterprise document asset into the knowledge base repository."""
    return DocumentRepository.create_document(db=db, req=req, user=current_user)


@router.patch("/documents/{document_id}", response_model=KnowledgeDocDetail)
def update_knowledge_document(
    document_id: int,
    req: KnowledgeDocUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Update document taxonomy, tags, department ownership, or version number."""
    return DocumentRepository.update_document(db=db, document_id=document_id, req=req)


@router.delete("/documents/{document_id}")
def delete_knowledge_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Executive"])),
):
    """Remove a document from the enterprise knowledge base."""
    return DocumentRepository.delete_document(db=db, document_id=document_id)


@router.get("/stats", response_model=KnowledgeStatsResponse)
def get_knowledge_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve aggregate knowledge base metrics, department distribution, and format statistics."""
    return DocumentRepository.get_repository_stats(db=db)
