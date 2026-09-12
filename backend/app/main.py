from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, SessionLocal, Base
from app.db import base  # Ensures all models are registered with Base metadata
from app.seed_data import seed_database
from app.api.v1.router import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegisiq.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to handle startup and shutdown sequences."""
    logger.info("Initializing AegisIQ Enterprise Platform Backend...")
    # Create DB schema if it doesn't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized.")
    
    # Run seed script for roles and demo users
    try:
        db = SessionLocal()
        seed_database(db=db)
        db.close()
    except Exception as e:
        logger.warning(f"Database seed notice: {e}")

    yield

    logger.info("Shutting down AegisIQ Backend Services...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Decision Intelligence Platform - REST API Layer",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

from fastapi.middleware.gzip import GZipMiddleware
from app.security_hardening.headers import SecurityHeadersMiddleware

# Configure Cross-Origin Resource Sharing (CORS) for Enterprise Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register OWASP Enterprise Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Register High-Speed GZip Response Compression Middleware (Compress responses > 1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)



# Mount API v1 Master Router
app.include_router(api_router, prefix=settings.API_V1_STR)


from fastapi.responses import JSONResponse, Response
from app.services.telemetry_service import TelemetryService
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/", include_in_schema=False)
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "api_docs": "/docs",
        "health_check": "/health",
        "metrics": "/metrics",
    }


@app.get("/health", tags=["Telemetry & Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "aegisiq-backend",
        "version": settings.VERSION,
        "runtime": "production",
    }


@app.get("/metrics", tags=["Telemetry & Health"], response_class=Response)
def root_metrics(db: Session = Depends(get_db)):
    content = TelemetryService.get_prometheus_exposition(db=db)
    return Response(content=content, media_type="text/plain; version=0.0.4")

