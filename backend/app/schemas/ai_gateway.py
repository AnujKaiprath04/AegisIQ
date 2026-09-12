from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai_gateway.types import LLMProviderType, ProviderStatus


class GatewayChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="User question or executive instruction")
    session_id: Optional[str] = None
    provider_type: Optional[LLMProviderType] = LLMProviderType.LOCAL_ENTERPRISE
    system_persona: Optional[str] = "CEO"
    temperature: Optional[float] = 0.2


class GatewayCitation(BaseModel):
    document_title: str
    section: str
    relevance_score: float


class GatewayChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    intent_confidence: float
    intent_explanation: str
    provider: str
    model_name: str
    latency_ms: float
    tokens_estimated: int
    citations: List[GatewayCitation] = []
    timestamp: str


class IntentClassifyRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)


class IntentClassifyResponse(BaseModel):
    prompt: str
    intent: str
    confidence: float
    explanation: str


class ProviderListResponse(BaseModel):
    active_default: str
    providers: List[ProviderStatus]


class GatewayTelemetryResponse(BaseModel):
    gateway_status: str
    total_requests_processed: int
    average_latency_ms: float
    active_providers_count: int
    uptime_pct: float
