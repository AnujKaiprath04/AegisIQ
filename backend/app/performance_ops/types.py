from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CacheNamespace(str, Enum):
    ALL = "ALL"
    BI_DASHBOARD = "BI_DASHBOARD"
    ML_PREDICTIONS = "ML_PREDICTIONS"
    RAG_EMBEDDINGS = "RAG_EMBEDDINGS"
    USER_SESSIONS = "USER_SESSIONS"


class CacheTierStats(BaseModel):
    tier_name: str
    hit_count: int
    miss_count: int
    hit_rate_pct: float
    memory_used_mb: float
    total_keys: int


class QueryOptimizationProfile(BaseModel):
    query_name: str
    table_name: str
    index_used: str
    unindexed_latency_ms: float
    optimized_latency_ms: float
    latency_reduction_pct: float


class PerformanceOverview(BaseModel):
    overall_cache_hit_rate_pct: float = 94.2
    p50_latency_ms: float = 6.2
    p90_latency_ms: float = 14.8
    p99_latency_ms: float = 28.5
    compression_ratio_pct: float = 78.4
    cache_tiers: List[CacheTierStats] = []
    query_profiles: List[QueryOptimizationProfile] = []
    timestamp: str


class CacheFlushRequest(BaseModel):
    namespace: CacheNamespace = Field(default=CacheNamespace.ALL, description="Cache namespace to invalidate")


class CacheFlushResult(BaseModel):
    status: str
    namespace: CacheNamespace
    flushed_keys_count: int
    timestamp: str
