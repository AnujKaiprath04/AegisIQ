from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertRuleDefinition(BaseModel):
    name: str
    expression: str
    duration: str
    severity: AlertSeverity
    summary: str
    description: str


class PrometheusMetricDefinition(BaseModel):
    name: str
    metric_type: str  # counter, gauge, histogram
    description: str
    current_value: float


class LogStreamEntry(BaseModel):
    timestamp: str
    level: str
    logger: str
    message: str
    trace_id: str
    span_id: str


class ObservabilityOverview(BaseModel):
    apm_status: str = "ONLINE_PROMETHEUS_LOKI_GRAFANA"
    total_metrics_tracked: int
    scrape_interval_seconds: int = 15
    active_alerts_count: int = 0
    metrics: List[PrometheusMetricDefinition] = []
    alert_rules: List[AlertRuleDefinition] = []
    timestamp: str
