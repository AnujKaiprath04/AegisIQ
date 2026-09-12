from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base


class KnowledgeBaseDocument(Base):
    __tablename__ = "knowledge_base_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(30), default="PDF", index=True)  # PDF, DOCX, PPTX, TXT, MARKDOWN, CSV
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")

    department = Column(String(50), default="EXECUTIVE", index=True)  # FINANCE, SECURITY, EXECUTIVE, LEGAL, ENGINEERING, HR, SALES
    category = Column(String(50), default="POLICY_GOVERNANCE", index=True)  # POLICY_GOVERNANCE, FINANCIAL_FILING, OPERATIONAL_RUNBOOK, TECHNICAL_SPEC, CONTRACT_SLA
    tags_json = Column(Text, default="[]")  # JSON serialized list of tags

    author = Column(String(150), default="Enterprise AI Knowledge Team")
    version = Column(String(30), default="v1.0")
    document_sha256 = Column(String(64), unique=True, nullable=True, index=True)

    status = Column(String(30), default="INDEXED", index=True)  # DRAFT, PROCESSING, INDEXED, ARCHIVED
    summary_text = Column(Text, nullable=True)

    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_indexed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    uploaded_by = relationship("User")

    def __repr__(self):
        return f"<KnowledgeBaseDocument(title='{self.title}', dept='{self.department}', ver='{self.version}')>"
