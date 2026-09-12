from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SubsystemHealth(BaseModel):
    name: str
    status: str  # HEALTHY, DEGRADED, OFFLINE
    latency_ms: float
    uptime_pct: float
    details: str


class SystemResourceMetrics(BaseModel):
    cpu_usage_pct: float
    memory_allocated_mb: float
    memory_total_mb: float
    memory_usage_pct: float
    disk_usage_pct: float
    uptime_seconds: int


class DatabasePoolMetrics(BaseModel):
    pool_size: int
    checked_in_connections: int
    checked_out_connections: int
    overflow_connections: int
    pool_utilization_pct: float
    avg_query_latency_ms: float


class APMLatencyMetrics(BaseModel):
    requests_per_second: float
    p50_latency_ms: float
    p90_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    status_2xx_pct: float
    status_4xx_pct: float
    status_5xx_pct: float


class FullTelemetrySnapshotResponse(BaseModel):
    platform_status: str  # OPERATIONAL, DEGRADED, MAINTENANCE
    timestamp: datetime
    subsystems: List[SubsystemHealth]
    resources: SystemResourceMetrics
    db_pool: DatabasePoolMetrics
    apm: APMLatencyMetrics
