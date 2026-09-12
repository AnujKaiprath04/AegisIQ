from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.docs_ops.types import (
    ArchitectureLayerInfo,
    DocSectionMetadata,
    DocumentationOverview,
    IncidentPlaybook,
)


class DocSectionMetadataSchema(DocSectionMetadata):
    pass


class ArchitectureLayerInfoSchema(ArchitectureLayerInfo):
    pass


class IncidentPlaybookSchema(IncidentPlaybook):
    pass


class DocumentationOverviewSchema(DocumentationOverview):
    pass


class DocsOverviewResponse(BaseModel):
    overview: DocumentationOverviewSchema


class ArchitectureResponse(BaseModel):
    total_layers: int
    layers: List[ArchitectureLayerInfoSchema] = []


class PlaybooksResponse(BaseModel):
    total_playbooks: int
    playbooks: List[IncidentPlaybookSchema] = []
