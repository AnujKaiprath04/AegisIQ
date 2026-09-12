import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.schemas.prompt_engine import (
    PromptPlaygroundRequest,
    PromptPlaygroundResponse,
    PromptRenderRequest,
    PromptRenderResponse,
    PromptTemplateCreate,
    PromptTemplateResponse,
)
from app.prompt_service.registry import PromptRegistry
from app.prompt_service.types import PromptCategory, PromptTemplate
from app.ai_gateway.providers import LLMProviderFactory

router = APIRouter(prefix="/ai/prompts", tags=["Part 2 - Module 8: Prompt Engineering Framework"])


@router.get("/templates", response_model=List[PromptTemplateResponse])
def list_prompt_templates(
    category: Optional[PromptCategory] = Query(None, description="Filter by category: SYSTEM, BUSINESS, REPORT, SUMMARY, RECOMMENDATION, SQL, REASONING, SECURITY"),
    current_user: User = Depends(get_current_user),
):
    """List all registered enterprise prompt templates in the library."""
    templates = PromptRegistry.list_templates(category=category)
    return [PromptTemplateResponse(**t.model_dump()) for t in templates]


@router.get("/templates/{name}", response_model=PromptTemplateResponse)
def get_prompt_template(
    name: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed prompt template specification, variables, and few-shot exemplars."""
    tpl = PromptRegistry.get_template(name)
    if not tpl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt template '{name}' not found.")
    return PromptTemplateResponse(**tpl.model_dump())


@router.post("/templates", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
def register_prompt_template(
    req: PromptTemplateCreate,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Register or version an enterprise prompt template in the registry."""
    new_tpl = PromptTemplate(
        id=f"prompt-custom-{int(time.time())}",
        name=req.name.upper(),
        category=req.category,
        version=req.version,
        template_text=req.template_text,
        input_variables=req.input_variables,
        description=req.description,
        author=req.author or current_user.full_name or "Enterprise User",
    )
    registered = PromptRegistry.register_template(new_tpl)
    return PromptTemplateResponse(**registered.model_dump())


@router.post("/render", response_model=PromptRenderResponse)
def render_prompt_template(
    req: PromptRenderRequest,
    current_user: User = Depends(get_current_user),
):
    """Interpolate template variables and format prompt payload with optional few-shot examples."""
    try:
        rendered = PromptRegistry.render_template(
            name=req.template_name,
            variables=req.variables,
            include_few_shots=req.include_few_shots,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    tokens = max(1, len(rendered.split()))
    return PromptRenderResponse(
        template_name=req.template_name,
        rendered_prompt=rendered,
        estimated_tokens=tokens,
    )


@router.post("/test-playground", response_model=PromptPlaygroundResponse)
def test_prompt_playground(
    req: PromptPlaygroundRequest,
    current_user: User = Depends(require_roles(["Admin", "Executive", "Data Analyst"])),
):
    """Render prompt template and execute live generation test against the active LLM."""
    start_time = time.time()
    try:
        rendered = PromptRegistry.render_template(
            name=req.template_name,
            variables=req.variables,
            include_few_shots=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    provider = LLMProviderFactory.get_provider()
    output = provider.generate(prompt=rendered, temperature=0.2)
    latency_ms = round((time.time() - start_time) * 1000 + 4.5, 2)

    return PromptPlaygroundResponse(
        template_name=req.template_name,
        rendered_prompt=rendered,
        generated_output=output,
        latency_ms=latency_ms,
    )
