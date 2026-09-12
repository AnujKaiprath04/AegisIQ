from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.business_api import (
    PlatformManifestResponse,
    ToolExecuteRequestSchema,
    ToolExecuteResponseSchema,
    ToolInfoResponse,
    UnifiedDecisionRequestSchema,
    UnifiedDecisionResponseSchema,
)
from app.tool_integration.registry import EnterpriseToolRegistry
from app.tool_integration.executor import ToolExecutionSandbox
from app.tool_integration.bridge import UnifiedDecisionBridge
from app.tool_integration.types import UnifiedDecisionRequest

router = APIRouter(prefix="/ai", tags=["Part 2 - Module 12: Business API Integration & Unified Decision Bridge"])


@router.get("/tools", response_model=List[ToolInfoResponse])
def list_business_tools(
    current_user: User = Depends(get_current_user),
):
    """List all registered enterprise business tools with JSON Schemas and required permissions."""
    tools = EnterpriseToolRegistry.list_tools()
    return [ToolInfoResponse(**t.model_dump()) for t in tools]


@router.post("/tools/execute", response_model=ToolExecuteResponseSchema)
def execute_business_tool(
    req: ToolExecuteRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Execute a registered business tool safely in the platform execution sandbox."""
    res = ToolExecutionSandbox.execute(
        tool_name=req.tool_name,
        arguments=req.arguments,
        user_roles=[r.name for r in current_user.roles] if current_user.roles else ["Viewer"],
    )
    return ToolExecuteResponseSchema(**res.model_dump())


@router.post("/decision-bridge/query", response_model=UnifiedDecisionResponseSchema)
def query_unified_decision_bridge(
    req: UnifiedDecisionRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Master Unified AI Decision Bridge executing multi-step reasoning, RAG grounding, tool calling, and compliance audit logging."""
    internal_req = UnifiedDecisionRequest(
        query=req.query,
        persona=req.persona or "CEO",
        session_id=req.session_id,
        enable_tools=req.enable_tools if req.enable_tools is not None else True,
    )
    res = UnifiedDecisionBridge.execute_unified_decision(
        req=internal_req,
        user_id=current_user.id,
        user_email=current_user.email,
        user_roles=[r.name for r in current_user.roles] if current_user.roles else ["Viewer"],
    )
    return UnifiedDecisionResponseSchema(**res.model_dump())


@router.get("/decision-bridge/manifest", response_model=PlatformManifestResponse)
def get_decision_platform_manifest(
    current_user: User = Depends(get_current_user),
):
    """Retrieve master capability manifest and operational status across all 12 modules of AegisIQ Part 2."""
    manifest = UnifiedDecisionBridge.get_platform_manifest()
    return PlatformManifestResponse(**manifest)
