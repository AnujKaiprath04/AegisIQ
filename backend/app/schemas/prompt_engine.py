from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.prompt_service.types import FewShotExample, PromptCategory, PromptTemplate


class PromptTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: PromptCategory
    version: str = Field(default="v1.0")
    template_text: str = Field(..., min_length=10)
    input_variables: List[str] = Field(default_factory=list)
    description: str = Field(..., min_length=5)
    author: Optional[str] = "Enterprise AI Team"


class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    category: PromptCategory
    version: str
    template_text: str
    input_variables: List[str] = []
    few_shot_examples: List[FewShotExample] = []
    description: str
    author: str
    is_active: bool


class PromptRenderRequest(BaseModel):
    template_name: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    include_few_shots: bool = True


class PromptRenderResponse(BaseModel):
    template_name: str
    rendered_prompt: str
    estimated_tokens: int


class PromptPlaygroundRequest(BaseModel):
    template_name: str
    variables: Dict[str, Any] = Field(default_factory=dict)


class PromptPlaygroundResponse(BaseModel):
    template_name: str
    rendered_prompt: str
    generated_output: str
    latency_ms: float
