from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeDocumentDetail,
    KnowledgeDocumentSummary,
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag_service import RAGService

router = APIRouter(prefix="/knowledge", tags=["Module 10: RAG & Vector Knowledge Base"])


@router.get("/documents", response_model=List[KnowledgeDocumentSummary])
def list_knowledge_documents(
    category: Optional[str] = Query(None, description="Filter by category: POLICY, FINANCIAL_FILING, SLA_CONTRACT, SECURITY_COMPLIANCE"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all indexed enterprise documents in the knowledge base."""
    return RAGService.get_documents(db=db, category=category)


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentDetail)
def get_document_details(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full document metadata and vector chunk breakdown."""
    return RAGService.get_document_detail(db=db, document_id=document_id)


@router.post("/upload", response_model=KnowledgeDocumentDetail, status_code=status.HTTP_201_CREATED)
def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("POLICY"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst", "Business Analyst"])),
):
    """Upload an unstructured document (PDF, DOCX, TXT, MD) and perform automatic chunking and vector indexing."""
    return RAGService.upload_and_index_document(
        db=db,
        file=file,
        title=title,
        category=category,
        user=current_user,
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
def delete_knowledge_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Data Analyst"])),
):
    """Delete a document and cascade remove all its associated vector chunk embeddings."""
    RAGService.delete_document(db=db, document_id=document_id)
    return {"message": f"Knowledge document {document_id} and associated vector embeddings removed."}


@router.post("/query", response_model=RAGQueryResponse)
def execute_rag_query(
    req: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute semantic vector retrieval and synthesize a citation-grounded response."""
    return RAGService.query_rag(db=db, req=req, user=current_user)
