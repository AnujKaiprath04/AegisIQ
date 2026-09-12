from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # PDF, DOCX, TXT, MD
    file_size_bytes = Column(BigInteger, default=0)
    total_chunks = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    category = Column(String(50), default="POLICY", index=True)  # POLICY, FINANCIAL_FILING, SLA_CONTRACT, SECURITY_COMPLIANCE
    storage_path = Column(String(500), nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    uploaded_by = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index.asc()")

    def __repr__(self):
        return f"<KnowledgeDocument(title='{self.title}', type='{self.file_type}', chunks={self.total_chunks})>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_json = Column(Text, nullable=True)  # Vector representation (e.g. JSON array of floats)
    page_number = Column(Integer, default=1)
    section_heading = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("KnowledgeDocument", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(doc_id={self.document_id}, idx={self.chunk_index}, tokens={self.token_count})>"


class RAGSearchQuery(Base):
    __tablename__ = "rag_search_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    query_text = Column(Text, nullable=False)
    top_k = Column(Integer, default=3)
    matched_chunks_count = Column(Integer, default=0)
    response_synthesis = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<RAGSearchQuery(query='{self.query_text[:30]}...', latency={self.latency_ms}ms)>"
