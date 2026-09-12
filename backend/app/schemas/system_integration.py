from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.system_integration.types import (
    CrossPartPipelineRequest,
    CrossPartPipelineResult,
    ServiceTopologyNode,
    SubsystemDetail,
    SystemHealthOverview,
)


class SubsystemDetailSchema(SubsystemDetail):
    pass


class SystemHealthOverviewSchema(SystemHealthOverview):
    pass


class CrossPartPipelineRequestSchema(CrossPartPipelineRequest):
    pass


class CrossPartPipelineResultSchema(CrossPartPipelineResult):
    pass


class ServiceTopologyNodeSchema(ServiceTopologyNode):
    pass


class SystemHealthResponse(BaseModel):
    health: SystemHealthOverviewSchema


class CrossPartPipelineResponse(BaseModel):
    pipeline: CrossPartPipelineResultSchema


class ServiceTopologyResponse(BaseModel):
    total_nodes: int
    nodes: List[ServiceTopologyNodeSchema] = []
