from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SubsystemStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class SubsystemDetail(BaseModel):
    name: str
    part: str = Field(..., description="Part 1, Part 2, or Part 3")
    status: SubsystemStatus
    latency_ms: float
    details: str


class SystemHealthOverview(BaseModel):
    overall_status: str
    total_subsystems: int
    operational_count: int
    subsystems: List[SubsystemDetail] = []
    timestamp: str


class CrossPartPipelineRequest(BaseModel):
    account_id: str = Field(default="ACC-APEX-001")
    company_name: str = Field(default="Apex Global Logistics")
    support_tickets_30d: int = Field(default=12, ge=0)
    nps_score: int = Field(default=4, ge=0, le=10)
    license_utilization_pct: float = Field(default=34.0, ge=0.0, le=100.0)
    arr_usd: float = Field(default=480000.0, ge=0.0)


class CrossPartPipelineResult(BaseModel):
    pipeline_id: str
    status: str
    execution_time_ms: float
    part1_account_data: Dict[str, Any]
    part3_prediction: Dict[str, Any]
    part3_xai_attribution: Dict[str, Any]
    part2_rag_playbook: Dict[str, Any]
    part2_ai_synthesis: str
    part3_alert_dispatched: Dict[str, Any]
    part1_audit_logged: bool


class ServiceTopologyNode(BaseModel):
    id: str
    name: str
    layer: str
    dependencies: List[str] = []
