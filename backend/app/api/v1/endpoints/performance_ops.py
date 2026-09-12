from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.performance_ops import (
    CacheFlushRequestSchema,
    CacheFlushResponse,
    CacheFlushResultSchema,
    CacheStatsResponse,
    CacheTierStatsSchema,
    PerformanceOverviewResponse,
    PerformanceOverviewSchema,
)
from app.performance_ops.engine import PerformanceOptimizationEngine

router = APIRouter(prefix="/ops/performance", tags=["Part 4 - Module 7: Performance Optimization"])


@router.get("/overview", response_model=PerformanceOverviewResponse)
def get_performance_overview(
    current_user: User = Depends(get_current_user),
):
    """Retrieve performance metrics, multi-tier cache hit rates (94.2%), and query latency profiles."""
    overview = PerformanceOptimizationEngine.get_overview()
    return PerformanceOverviewResponse(overview=PerformanceOverviewSchema(**overview.model_dump()))


@router.get("/cache", response_model=CacheStatsResponse)
def get_cache_tier_stats(
    current_user: User = Depends(get_current_user),
):
    """Retrieve L1 (In-Memory) and L2 (Distributed Redis) cache tier hit rates, memory usages, and key counts."""
    stats = PerformanceOptimizationEngine.get_cache_stats()
    return CacheStatsResponse(
        total_tiers=len(stats),
        tiers=[CacheTierStatsSchema(**s.model_dump()) for s in stats],
    )


@router.post("/cache/flush", response_model=CacheFlushResponse)
def flush_cache_namespace(
    req: CacheFlushRequestSchema,
    current_user: User = Depends(get_current_user),
):
    """Invalidate specific cache namespaces (BI_DASHBOARD, ML_PREDICTIONS, RAG_EMBEDDINGS, ALL)."""
    result = PerformanceOptimizationEngine.flush_cache(req)
    return CacheFlushResponse(result=CacheFlushResultSchema(**result.model_dump()))
