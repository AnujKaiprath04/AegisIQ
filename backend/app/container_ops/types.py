from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServiceContainerSpec(BaseModel):
    service_name: str
    image_base: str
    exposed_port: int
    user_uid: int
    user_name: str
    multi_stage_build: bool = True
    healthcheck_configured: bool = True
    cpu_limit: str
    memory_limit: str


class ContainerArchitectureOverview(BaseModel):
    architecture: str = "Multi-Container Micro-Service Pod"
    network_bridge: str = "aegisiq-network"
    total_containers: int
    services: List[ServiceContainerSpec] = []


class RuntimeContainerHealth(BaseModel):
    container_status: str
    uptime_seconds: float
    memory_usage_mb: float
    cpu_utilization_pct: float
    liveness_probe_status: str
    readiness_probe_status: str
    timestamp: str
