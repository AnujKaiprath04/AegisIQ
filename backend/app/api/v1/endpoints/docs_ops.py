from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.docs_ops import (
    ArchitectureLayerInfoSchema,
    ArchitectureResponse,
    DocsOverviewResponse,
    DocumentationOverviewSchema,
    IncidentPlaybookSchema,
    PlaybooksResponse,
)
from app.docs_ops.engine import EnterpriseDocumentationEngine

router = APIRouter(prefix="/ops/docs", tags=["Part 4 - Module 9: Documentation"])


@router.get("/overview", response_model=DocsOverviewResponse)
def get_documentation_overview(
    current_user: User = Depends(get_current_user),
):
    """Retrieve full platform documentation suite catalog, file paths, and section metadata."""
    overview = EnterpriseDocumentationEngine.get_overview()
    return DocsOverviewResponse(overview=DocumentationOverviewSchema(**overview.model_dump()))


@router.get("/architecture", response_model=ArchitectureResponse)
def get_architecture_layers(
    current_user: User = Depends(get_current_user),
):
    """List 5 enterprise architectural layers, technology stacks, and responsibilities."""
    layers = EnterpriseDocumentationEngine.get_architecture()
    return ArchitectureResponse(
        total_layers=len(layers),
        layers=[ArchitectureLayerInfoSchema(**l.model_dump()) for l in layers],
    )


@router.get("/runbook-topics", response_model=PlaybooksResponse)
def get_incident_playbooks(
    current_user: User = Depends(get_current_user),
):
    """List platform administrator incident response playbooks and emergency mitigation procedures."""
    playbooks = EnterpriseDocumentationEngine.get_playbooks()
    return PlaybooksResponse(
        total_playbooks=len(playbooks),
        playbooks=[IncidentPlaybookSchema(**p.model_dump()) for p in playbooks],
    )
