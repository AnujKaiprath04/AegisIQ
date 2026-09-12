from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.performance_ops.types import (
    CacheFlushRequest,
    CacheFlushResult,
    CacheTierStats,
    PerformanceOverview,
    QueryOptimizationProfile,
)


class CacheTierStatsSchema(CacheTierStats):
    pass


class QueryOptimizationProfileSchema(QueryOptimizationProfile):
    pass


class PerformanceOverviewSchema(PerformanceOverview):
    pass


class CacheFlushRequestSchema(CacheFlushRequest):
    pass


class CacheFlushResultSchema(CacheFlushResult):
    pass


class PerformanceOverviewResponse(BaseModel):
    overview: PerformanceOverviewSchema


class CacheStatsResponse(BaseModel):
    total_tiers: int
    tiers: List[CacheTierStatsSchema] = []


class CacheFlushResponse(BaseModel):
    result: CacheFlushResultSchema
