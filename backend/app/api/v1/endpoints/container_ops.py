from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.container_ops import (
    ContainerArchitectureOverviewSchema,
    ContainerHealthResponse,
    ContainerSpecResponse,
    RuntimeContainerHealthSchema,
)
from app.container_ops.engine import ContainerDiagnosticsEngine

router = APIRouter(prefix="/ops/container", tags=["Part 4 - Module 2: Containerization"])


@router.get("/spec", response_model=ContainerSpecResponse)
def get_container_specs(
    current_user: User = Depends(get_current_user),
):
    """Retrieve multi-container pod specifications, non-root UIDs, and resource bounds."""
    specs = ContainerDiagnosticsEngine.get_container_specs()
    return ContainerSpecResponse(overview=ContainerArchitectureOverviewSchema(**specs.model_dump()))


@router.get("/health", response_model=ContainerHealthResponse)
def get_container_runtime_health():
    """Liveness and readiness probe for Docker Compose and Kubernetes container orchestrators (public health check)."""
    health = ContainerDiagnosticsEngine.get_runtime_health()
    return ContainerHealthResponse(health=RuntimeContainerHealthSchema(**health.model_dump()))
