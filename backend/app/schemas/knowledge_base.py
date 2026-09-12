from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.document_service.types import CategoryType, DepartmentType, DocumentStatus, FileFormat


class KnowledgeDocCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    file_name: str = Field(..., min_length=2, max_length=255)
    original_filename: str = Field(..., min_length=2, max_length=255)
    file_format: str = Field(default="PDF")
    file_size_bytes: int = Field(default=0)
    mime_type: str = Field(default="application/pdf")
    department: str = Field(default="EXECUTIVE")
    category: str = Field(default="POLICY_GOVERNANCE")
    tags: List[str] = Field(default_factory=list)
    author: str = Field(default="Enterprise AI Knowledge Team")
    version: str = Field(default="v1.0")
    summary_text: Optional[str] = None


class KnowledgeDocUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    status: Optional[str] = None
    summary_text: Optional[str] = None


class KnowledgeDocSummary(BaseModel):
    id: int
    title: str
    file_name: str
    file_format: str
    file_size_bytes: int
    department: str
    category: str
    tags: List[str] = []
    author: str
    version: str
    document_sha256: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeDocDetail(KnowledgeDocSummary):
    original_filename: str
    mime_type: str
    summary_text: Optional[str] = None
    last_indexed_at: Optional[datetime] = None


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    total_storage_mb: float
    indexed_count: int
    department_counts: Dict[str, int] = {}
    format_counts: Dict[str, int] = {}
