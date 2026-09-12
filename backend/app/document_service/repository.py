import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.knowledge_base import KnowledgeBaseDocument
from app.models.user import User
from app.schemas.knowledge_base import (
    KnowledgeDocCreate,
    KnowledgeDocDetail,
    KnowledgeDocSummary,
    KnowledgeDocUpdate,
    KnowledgeStatsResponse,
)

logger = logging.getLogger("aegisiq.document_service.repository")

SEEDED_KNOWLEDGE_DOCS = [
    {
        "title": "ISO/IEC 27001:2022 Enterprise Information Security Policy",
        "file_name": "ISO_27001_Enterprise_Security_Standard.pdf",
        "original_filename": "ISO_27001_Enterprise_Security_Standard.pdf",
        "file_format": "PDF",
        "file_size_bytes": 2450000,
        "mime_type": "application/pdf",
        "department": "SECURITY",
        "category": "POLICY_GOVERNANCE",
        "tags_json": json.dumps(["iso-27001", "infosec", "compliance", "access-control"]),
        "author": "Chief Information Security Officer (CISO)",
        "version": "v2.1",
        "document_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "status": "INDEXED",
        "summary_text": "Mandatory enterprise information security policies, cryptographic key governance, and role-based access control guidelines.",
    },
    {
        "title": "Q1 2026 Strategic Financial Report & ARR Telemetry",
        "file_name": "Q1_2026_Executive_Financial_Filing.xlsx",
        "original_filename": "Q1_2026_Executive_Financial_Filing.xlsx",
        "file_format": "CSV",
        "file_size_bytes": 1120000,
        "mime_type": "text/csv",
        "department": "FINANCE",
        "category": "FINANCIAL_FILING",
        "tags_json": json.dumps(["financials", "arr", "margin", "q1-2026"]),
        "author": "VP Strategic Finance & Treasury",
        "version": "v1.0",
        "document_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        "status": "INDEXED",
        "summary_text": "Audited Q1 2026 general ledger performance, customer expansion metrics, EBITDA variance, and ARR trajectory.",
    },
    {
        "title": "Master Enterprise Service Level Agreement (SLA) & Incident Protocol",
        "file_name": "Master_Enterprise_SLA_Handbook.docx",
        "original_filename": "Master_Enterprise_SLA_Handbook.docx",
        "file_format": "DOCX",
        "file_size_bytes": 840000,
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "department": "LEGAL",
        "category": "CONTRACT_SLA",
        "tags_json": json.dumps(["sla", "uptime", "legal", "incident-response"]),
        "author": "Office of General Counsel",
        "version": "v3.0",
        "document_sha256": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
        "status": "INDEXED",
        "summary_text": "Tier-1 enterprise contractual uptime commitments (99.99%), severity escalation matrices, and remediation remedies.",
    },
    {
        "title": "Cloud Infrastructure Zero-Trust & Disaster Recovery Runbook",
        "file_name": "Cloud_Disaster_Recovery_Runbook.md",
        "original_filename": "Cloud_Disaster_Recovery_Runbook.md",
        "file_format": "MARKDOWN",
        "file_size_bytes": 410000,
        "mime_type": "text/markdown",
        "department": "ENGINEERING",
        "category": "OPERATIONAL_RUNBOOK",
        "tags_json": json.dumps(["devops", "disaster-recovery", "kubernetes", "zero-trust"]),
        "author": "Principal DevOps Architect",
        "version": "v1.4",
        "document_sha256": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
        "status": "INDEXED",
        "summary_text": "Multi-region failover automation, database replication failback, and ingress TLS gateway recovery procedures.",
    },
    {
        "title": "Q2 2026 Board of Directors Strategic Expansion Deck",
        "file_name": "Q2_2026_Executive_Strategy_Deck.pptx",
        "original_filename": "Q2_2026_Executive_Strategy_Deck.pptx",
        "file_format": "PPTX",
        "file_size_bytes": 3850000,
        "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "department": "EXECUTIVE",
        "category": "EXECUTIVE_STRATEGY",
        "tags_json": json.dumps(["strategy", "boardroom", "expansion", "q2-2026"]),
        "author": "Chief Executive Officer (CEO)",
        "version": "v1.0",
        "document_sha256": "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35",
        "status": "INDEXED",
        "summary_text": "Strategic market expansion vectors, AI adoption milestones, and enterprise capital allocation roadmap for 2026-2027.",
    },
]


class DocumentRepository:
    @staticmethod
    def seed_initial_documents(db: Session):
        """Seed default enterprise knowledge base document repository."""
        for doc_spec in SEEDED_KNOWLEDGE_DOCS:
            existing = db.query(KnowledgeBaseDocument).filter(
                KnowledgeBaseDocument.file_name == doc_spec["file_name"]
            ).first()
            if not existing:
                db.add(KnowledgeBaseDocument(**doc_spec))
        db.commit()

    @staticmethod
    def _to_summary(doc: KnowledgeBaseDocument) -> KnowledgeDocSummary:
        tags = []
        if doc.tags_json:
            try:
                tags = json.loads(doc.tags_json)
            except Exception:
                tags = []
        return KnowledgeDocSummary(
            id=doc.id,
            title=doc.title,
            file_name=doc.file_name,
            file_format=doc.file_format,
            file_size_bytes=doc.file_size_bytes,
            department=doc.department,
            category=doc.category,
            tags=tags,
            author=doc.author,
            version=doc.version,
            document_sha256=doc.document_sha256,
            status=doc.status,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    @staticmethod
    def _to_detail(doc: KnowledgeBaseDocument) -> KnowledgeDocDetail:
        summary = DocumentRepository._to_summary(doc)
        return KnowledgeDocDetail(
            **summary.model_dump(),
            original_filename=doc.original_filename,
            mime_type=doc.mime_type,
            summary_text=doc.summary_text,
            last_indexed_at=doc.last_indexed_at,
        )

    @staticmethod
    def get_documents(
        db: Session,
        department: Optional[str] = None,
        category: Optional[str] = None,
        file_format: Optional[str] = None,
        search_query: Optional[str] = None,
        tag: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[KnowledgeDocSummary]:
        DocumentRepository.seed_initial_documents(db)
        query = db.query(KnowledgeBaseDocument)

        if department and department != "ALL":
            query = query.filter(KnowledgeBaseDocument.department == department.upper())
        if category and category != "ALL":
            query = query.filter(KnowledgeBaseDocument.category == category.upper())
        if file_format and file_format != "ALL":
            query = query.filter(KnowledgeBaseDocument.file_format == file_format.upper())
        if status_filter and status_filter != "ALL":
            query = query.filter(KnowledgeBaseDocument.status == status_filter.upper())
        if tag:
            query = query.filter(KnowledgeBaseDocument.tags_json.contains(f'"{tag}"'))
        if search_query:
            term = f"%{search_query}%"
            query = query.filter(
                or_(
                    KnowledgeBaseDocument.title.ilike(term),
                    KnowledgeBaseDocument.file_name.ilike(term),
                    KnowledgeBaseDocument.summary_text.ilike(term),
                )
            )

        docs = query.order_by(KnowledgeBaseDocument.created_at.desc()).all()
        return [DocumentRepository._to_summary(d) for d in docs]

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> KnowledgeDocDetail:
        doc = db.query(KnowledgeBaseDocument).filter(KnowledgeBaseDocument.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Knowledge document {document_id} not found.")
        return DocumentRepository._to_detail(doc)

    @staticmethod
    def create_document(
        db: Session,
        req: KnowledgeDocCreate,
        user: Optional[User] = None,
    ) -> KnowledgeDocDetail:
        # Calculate deterministic SHA-256 for document metadata uniqueness
        raw_hash_seed = f"{req.title}:{req.file_name}:{req.version}:{datetime.now(timezone.utc).isoformat()}"
        sha256_hash = hashlib.sha256(raw_hash_seed.encode("utf-8")).hexdigest()

        doc = KnowledgeBaseDocument(
            title=req.title,
            file_name=req.file_name,
            original_filename=req.original_filename,
            file_format=req.file_format.upper(),
            file_size_bytes=req.file_size_bytes,
            mime_type=req.mime_type,
            department=req.department.upper(),
            category=req.category.upper(),
            tags_json=json.dumps(req.tags),
            author=req.author,
            version=req.version,
            document_sha256=sha256_hash,
            status="INDEXED",
            summary_text=req.summary_text or f"Enterprise {req.department} document registered in AegisIQ knowledge repository.",
            uploaded_by_user_id=user.id if user else None,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return DocumentRepository._to_detail(doc)

    @staticmethod
    def update_document(
        db: Session,
        document_id: int,
        req: KnowledgeDocUpdate,
    ) -> KnowledgeDocDetail:
        doc = db.query(KnowledgeBaseDocument).filter(KnowledgeBaseDocument.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Knowledge document {document_id} not found.")

        if req.title is not None:
            doc.title = req.title
        if req.department is not None:
            doc.department = req.department.upper()
        if req.category is not None:
            doc.category = req.category.upper()
        if req.tags is not None:
            doc.tags_json = json.dumps(req.tags)
        if req.version is not None:
            doc.version = req.version
        if req.status is not None:
            doc.status = req.status.upper()
        if req.summary_text is not None:
            doc.summary_text = req.summary_text

        doc.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(doc)
        return DocumentRepository._to_detail(doc)

    @staticmethod
    def delete_document(db: Session, document_id: int) -> Dict[str, Any]:
        doc = db.query(KnowledgeBaseDocument).filter(KnowledgeBaseDocument.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Knowledge document {document_id} not found.")
        db.delete(doc)
        db.commit()
        return {"message": f"Document '{doc.title}' deleted successfully.", "id": document_id}

    @staticmethod
    def get_repository_stats(db: Session) -> KnowledgeStatsResponse:
        DocumentRepository.seed_initial_documents(db)
        docs = db.query(KnowledgeBaseDocument).all()
        
        dept_counts: Dict[str, int] = {}
        format_counts: Dict[str, int] = {}
        total_size_bytes = 0
        indexed_count = 0

        for d in docs:
            dept_counts[d.department] = dept_counts.get(d.department, 0) + 1
            format_counts[d.file_format] = format_counts.get(d.file_format, 0) + 1
            total_size_bytes += d.file_size_bytes or 0
            if d.status == "INDEXED":
                indexed_count += 1

        total_storage_mb = round(total_size_bytes / (1024 * 1024), 2)

        return KnowledgeStatsResponse(
            total_documents=len(docs),
            total_storage_mb=total_storage_mb,
            indexed_count=indexed_count,
            department_counts=dept_counts,
            format_counts=format_counts,
        )
