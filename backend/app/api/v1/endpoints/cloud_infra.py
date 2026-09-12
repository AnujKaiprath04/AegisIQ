from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.cloud_infra import (
    CloudDatabaseResponse,
    CloudInfrastructureTopologySchema,
    CloudStorageResponse,
    CloudTopologyResponse,
    DatabaseTopologyInfoSchema,
    StorageBucketConfigSchema,
)
from app.cloud_infra.engine import CloudInfrastructureManager

router = APIRouter(prefix="/infra/cloud", tags=["Part 4 - Module 3: Cloud Infrastructure"])


@router.get("/topology", response_model=CloudTopologyResponse)
def get_cloud_topology(
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive multi-cloud infrastructure topology (Vercel, Render, Neon, Supabase, K8s)."""
    top = CloudInfrastructureManager.get_topology()
    return CloudTopologyResponse(topology=CloudInfrastructureTopologySchema(**top.model_dump()))


@router.get("/storage", response_model=CloudStorageResponse)
def get_cloud_storage_status(
    current_user: User = Depends(get_current_user),
):
    """Retrieve cloud object storage buckets, capacities, and access control policies."""
    buckets = CloudInfrastructureManager.get_storage_buckets()
    return CloudStorageResponse(
        total_buckets=len(buckets),
        buckets=[StorageBucketConfigSchema(**b.model_dump()) for b in buckets],
    )


@router.get("/database", response_model=CloudDatabaseResponse)
def get_cloud_database_status(
    current_user: User = Depends(get_current_user),
):
    """Retrieve Neon serverless PostgreSQL connection pooling and autoscaling status."""
    db_info = CloudInfrastructureManager.get_database_info()
    return CloudDatabaseResponse(database=DatabaseTopologyInfoSchema(**db_info.model_dump()))
