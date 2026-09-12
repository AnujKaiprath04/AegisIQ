from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocSectionMetadata(BaseModel):
    doc_id: str
    title: str
    filename: str
    description: str
    total_sections: int
    format: str = "Markdown (GFM)"
    status: str = "APPROVED"


class ArchitectureLayerInfo(BaseModel):
    layer_name: str
    technology_stack: str
    responsibilities: List[str] = []
    mermaid_diagram_snippet: Optional[str] = None


class IncidentPlaybook(BaseModel):
    playbook_id: str
    alert_name: str
    severity: str
    trigger_condition: str
    mitigation_steps: List[str] = []


class DocumentationOverview(BaseModel):
    total_documents: int
    total_architectural_layers: int
    total_incident_playbooks: int
    documents: List[DocSectionMetadata] = []
    timestamp: str
