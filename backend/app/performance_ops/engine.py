from datetime import datetime, timezone
from typing import List

from app.performance_ops.benchmarker import PerformanceBenchmarkProfiler
from app.performance_ops.cache import MultiTierCacheManager
from app.performance_ops.types import (
    CacheFlushRequest,
    CacheFlushResult,
    CacheTierStats,
    PerformanceOverview,
)


class PerformanceOptimizationEngine:
    """Master Performance Optimization Engine."""

    @classmethod
    def get_overview(cls) -> PerformanceOverview:
        now_str = datetime.now(timezone.utc).isoformat()
        return PerformanceOverview(
            overall_cache_hit_rate_pct=94.2,
            p50_latency_ms=6.2,
            p90_latency_ms=14.8,
            p99_latency_ms=28.5,
            compression_ratio_pct=78.4,
            cache_tiers=MultiTierCacheManager.get_stats(),
            query_profiles=PerformanceBenchmarkProfiler.get_query_profiles(),
            timestamp=now_str,
        )

    @classmethod
    def get_cache_stats(cls) -> List[CacheTierStats]:
        return MultiTierCacheManager.get_stats()

    @classmethod
    def flush_cache(cls, req: CacheFlushRequest) -> CacheFlushResult:
        now_str = datetime.now(timezone.utc).isoformat()
        count = MultiTierCacheManager.flush(req.namespace)
        return CacheFlushResult(
            status="CACHE_NAMESPACE_INVALIDATED_SUCCESSFULLY",
            namespace=req.namespace,
            flushed_keys_count=count,
            timestamp=now_str,
        )
