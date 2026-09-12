from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/system", tags=["System & Health"])


@router.get("/health", summary="Health Check Endpoint")
def health_check(db: Session = Depends(get_db)):
    """Check backend and database health status."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
