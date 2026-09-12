from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.container_ops.types import (
    ContainerArchitectureOverview,
    RuntimeContainerHealth,
    ServiceContainerSpec,
)


class ServiceContainerSpecSchema(ServiceContainerSpec):
    pass


class ContainerArchitectureOverviewSchema(ContainerArchitectureOverview):
    pass


class RuntimeContainerHealthSchema(RuntimeContainerHealth):
    pass


class ContainerSpecResponse(BaseModel):
    overview: ContainerArchitectureOverviewSchema


class ContainerHealthResponse(BaseModel):
    health: RuntimeContainerHealthSchema
