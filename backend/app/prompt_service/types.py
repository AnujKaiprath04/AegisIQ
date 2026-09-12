from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PromptCategory(str, Enum):
    SYSTEM = "SYSTEM"
    BUSINESS = "BUSINESS"
    REPORT = "REPORT"
    SUMMARY = "SUMMARY"
    RECOMMENDATION = "RECOMMENDATION"
    SQL = "SQL"
    REASONING = "REASONING"
    SECURITY = "SECURITY"


class FewShotExample(BaseModel):
    user_input: str
    ideal_output: str
    context: Optional[str] = None


class PromptTemplate(BaseModel):
    id: str
    name: str
    category: PromptCategory
    version: str = "v1.0"
    template_text: str
    input_variables: List[str] = []
    few_shot_examples: List[FewShotExample] = []
    description: str
    author: str = "AegisIQ AI Engineering Team"
    is_active: bool = True
