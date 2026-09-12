from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.cicd_ops import (
    CIPipelineRunSchema,
    CIPipelineRunsResponse,
    DeploymentReleaseRecordSchema,
    DeploymentReleasesResponse,
    RollbackRequestSchema,
    RollbackResponse,
    RollbackResultSchema,
)
from app.cicd_ops.engine import CICDDiagnosticsEngine

router = APIRouter(prefix="/ops/cicd", tags=["Part 4 - Module 4: CI/CD Pipeline"])


@router.get("/runs", response_model=CIPipelineRunsResponse)
def get_cicd_pipeline_runs(
    current_user: User = Depends(get_current_user),
):
    """Retrieve CI/CD execution pipeline history across test matrices and linting jobs."""
    runs = CICDDiagnosticsEngine.get_pipeline_runs()
    return CIPipelineRunsResponse(
        total_runs=len(runs),
        runs=[CIPipelineRunSchema(**r.model_dump()) for r in runs],
    )


@router.get("/releases", response_model=DeploymentReleasesResponse)
def get_deployment_releases(
    current_user: User = Depends(get_current_user),
):
    """List deployment release history and Docker container image digests."""
    releases = CICDDiagnosticsEngine.get_releases()
    return DeploymentReleasesResponse(
        total_releases=len(releases),
        releases=[DeploymentReleaseRecordSchema(**rel.model_dump()) for rel in releases],
    )


@router.post("/rollback", response_model=RollbackResponse)
def trigger_deployment_rollback(
    req: RollbackRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Trigger zero-downtime automated rollback to a previous stable release tag and Docker digest."""
    result = CICDDiagnosticsEngine.trigger_rollback(req)
    return RollbackResponse(result=RollbackResultSchema(**result.model_dump()))
