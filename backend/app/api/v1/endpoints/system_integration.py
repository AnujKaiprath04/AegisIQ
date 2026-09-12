from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.system_integration import (
    CrossPartPipelineRequestSchema,
    CrossPartPipelineResponse,
    CrossPartPipelineResultSchema,
    ServiceTopologyNodeSchema,
    ServiceTopologyResponse,
    SystemHealthOverviewSchema,
    SystemHealthResponse,
)
from app.system_integration.engine import EnterpriseSystemIntegrationEngine

router = APIRouter(prefix="/integration/system", tags=["Part 4 - Module 1: System Integration"])


@router.get("/health", response_model=SystemHealthResponse)
def get_system_integration_health(
    current_user: User = Depends(get_current_user),
):
    """Retrieve comprehensive multi-part subsystem health check across Part 1, Part 2, and Part 3."""
    overview = EnterpriseSystemIntegrationEngine.check_health()
    return SystemHealthResponse(health=SystemHealthOverviewSchema(**overview.model_dump()))


@router.post("/master-pipeline", response_model=CrossPartPipelineResponse)
def execute_master_cross_part_pipeline(
    req: CrossPartPipelineRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Execute end-to-end scenario pipeline coordinating Part 1 ETL, Part 3 Predictive ML & XAI, Part 2 RAG & Copilot, and Part 1 Audit."""
    result = EnterpriseSystemIntegrationEngine.run_master_pipeline(req)
    return CrossPartPipelineResponse(pipeline=CrossPartPipelineResultSchema(**result.model_dump()))


@router.get("/topology", response_model=ServiceTopologyResponse)
def get_service_topology(
    current_user: User = Depends(get_current_user),
):
    """Retrieve service topology graph and inter-service dependencies."""
    nodes = EnterpriseSystemIntegrationEngine.get_topology()
    return ServiceTopologyResponse(
        total_nodes=len(nodes),
        nodes=[ServiceTopologyNodeSchema(**n.model_dump()) for n in nodes],
    )
