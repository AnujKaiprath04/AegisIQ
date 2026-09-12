from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMProviderType(str, Enum):
    GEMINI = "GEMINI"
    OPENAI = "OPENAI"
    GROQ = "GROQ"
    LOCAL_ENTERPRISE = "LOCAL_ENTERPRISE"


class QueryIntent(str, Enum):
    ENTERPRISE_RAG = "ENTERPRISE_RAG"
    BUSINESS_ANALYTICS = "BUSINESS_ANALYTICS"
    EXECUTIVE_REPORT = "EXECUTIVE_REPORT"
    CONVERSATIONAL_QA = "CONVERSATIONAL_QA"
    SQL_SYNTHESIS = "SQL_SYNTHESIS"


class GatewayMessage(BaseModel):
    role: str = Field(..., description="user, assistant, system")
    content: str


class ProviderStatus(BaseModel):
    provider_type: LLMProviderType
    display_name: str
    model_name: str
    is_available: bool = True
    latency_benchmark_ms: float = 0.0
    context_window_tokens: int = 128000

