from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.models.audit import UserActivityLog
from app.schemas.audit import AuditLogListResponse, AuditLogResponse, AuditStatsResponse

router = APIRouter(prefix="/audit", tags=["Security & Audit Logs"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Query paginated security activity audit logs with filters."""
    query = db.query(UserActivityLog)

    if action:
        query = query.filter(UserActivityLog.action.ilike(f"%{action}%"))
    if user_email:
        query = query.filter(UserActivityLog.user_email.ilike(f"%{user_email}%"))
    if status_filter:
        query = query.filter(UserActivityLog.status == status_filter.upper())

    total_count = query.count()
    logs = query.order_by(desc(UserActivityLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=AuditStatsResponse)
def get_audit_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
):
    """Admin-only: Aggregate metrics on platform events, failures, and active actors."""
    total_events = db.query(func.count(UserActivityLog.id)).scalar() or 0
    success_count = db.query(func.count(UserActivityLog.id)).filter(UserActivityLog.status == "SUCCESS").scalar() or 0
    failed_count = db.query(func.count(UserActivityLog.id)).filter(UserActivityLog.status == "FAILED").scalar() or 0
    warning_count = db.query(func.count(UserActivityLog.id)).filter(UserActivityLog.status == "WARNING").scalar() or 0

    # Top 5 actions
    top_actions_raw = (
        db.query(UserActivityLog.action, func.count(UserActivityLog.id).label("cnt"))
        .group_by(UserActivityLog.action)
        .order_by(desc("cnt"))
        .limit(5)
        .all()
    )
    top_actions = [{"action": a, "count": c} for a, c in top_actions_raw]

    # Top 5 recent active actors
    recent_actors_raw = (
        db.query(UserActivityLog.user_email, func.count(UserActivityLog.id).label("cnt"))
        .filter(UserActivityLog.user_email.isnot(None))
        .group_by(UserActivityLog.user_email)
        .order_by(desc("cnt"))
        .limit(5)
        .all()
    )
    recent_actors = [{"email": e, "event_count": c} for e, c in recent_actors_raw]

    return AuditStatsResponse(
        total_events=total_events,
        success_count=success_count,
        failed_count=failed_count,
        warning_count=warning_count,
        top_actions=top_actions,
        recent_actors=recent_actors,
    )
