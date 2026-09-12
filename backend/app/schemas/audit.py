from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total_count: int
    page: int
    page_size: int


class AuditStatsResponse(BaseModel):
    total_events: int
    success_count: int
    failed_count: int
    warning_count: int
    top_actions: List[Dict[str, Any]]
    recent_actors: List[Dict[str, Any]]
