from typing import List

from app.system_integration.types import (
    CrossPartPipelineRequest,
    CrossPartPipelineResult,
    ServiceTopologyNode,
    SystemHealthOverview,
)
from app.system_integration.health_checker import SystemIntegrationHealthChecker
from app.system_integration.pipeline_orchestrator import MasterCrossPartPipelineOrchestrator

SERVICE_TOPOLOGY: List[ServiceTopologyNode] = [
    ServiceTopologyNode(id="layer-frontend", name="Next.js & React Frontend Dashboard", layer="Presentation Layer", dependencies=["layer-gateway"]),
    ServiceTopologyNode(id="layer-gateway", name="FastAPI Master Enterprise Gateway", layer="API Gateway Layer", dependencies=["layer-part1", "layer-part2", "layer-part3"]),
    ServiceTopologyNode(id="layer-part1", name="Part 1: Core Platform, Auth, ETL & Database", layer="Enterprise Platform Core", dependencies=["layer-db"]),
    ServiceTopologyNode(id="layer-part2", name="Part 2: Generative AI, RAG & Copilot", layer="Cognitive AI Layer", dependencies=["layer-vector", "layer-llm"]),
    ServiceTopologyNode(id="layer-part3", name="Part 3: Machine Learning, XAI & SIEM", layer="Predictive & Security Intelligence", dependencies=["layer-part1", "layer-part2"]),
    ServiceTopologyNode(id="layer-db", name="PostgreSQL Relational Storage", layer="Data Persistence", dependencies=[]),
    ServiceTopologyNode(id="layer-vector", name="Vector Similarity Store", layer="Vector Memory", dependencies=[]),
    ServiceTopologyNode(id="layer-llm", name="LLM Providers (Google Gemini / Groq)", layer="External Foundation Models", dependencies=[]),
]


class EnterpriseSystemIntegrationEngine:
    """Master System Integration Engine unifying Parts 1, 2, and 3."""

    @classmethod
    def check_health(cls) -> SystemHealthOverview:
        return SystemIntegrationHealthChecker.evaluate_system_health()

    @classmethod
    def run_master_pipeline(cls, req: CrossPartPipelineRequest) -> CrossPartPipelineResult:
        return MasterCrossPartPipelineOrchestrator.execute_cross_part_pipeline(req)

    @classmethod
    def get_topology(cls) -> List[ServiceTopologyNode]:
        return SERVICE_TOPOLOGY
