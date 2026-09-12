from datetime import datetime, timezone
from typing import List

from app.monitoring_logging.logger import StructuredEnterpriseLogger
from app.monitoring_logging.metrics import PrometheusMetricsRegistry
from app.monitoring_logging.types import (
    AlertRuleDefinition,
    AlertSeverity,
    LogStreamEntry,
    ObservabilityOverview,
)

ALERT_RULES: List[AlertRuleDefinition] = [
    AlertRuleDefinition(
        name="HighHttpErrorRate",
        expression='(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100 > 5',
        duration="2m",
        severity=AlertSeverity.CRITICAL,
        summary="Elevated HTTP 5xx error rate on AegisIQ Backend",
        description="HTTP 5xx error rate exceeds 5% over a 5-minute sliding window.",
    ),
    AlertRuleDefinition(
        name="ElevatedApiLatencyP99",
        expression="histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.500",
        duration="3m",
        severity=AlertSeverity.WARNING,
        summary="P99 API response latency exceeds 500ms SLA",
        description="P99 response time has exceeded 500ms for more than 3 consecutive minutes.",
    ),
    AlertRuleDefinition(
        name="PostgresConnectionPoolHigh",
        expression="(pg_stat_activity_count / pg_settings_max_connections) * 100 > 85",
        duration="2m",
        severity=AlertSeverity.CRITICAL,
        summary="PostgreSQL active connection pool exceeds 85%",
        description="Active client connections exceed 85% of total pool capacity.",
    ),
    AlertRuleDefinition(
        name="ModelPredictionDriftAnomaly",
        expression="aegisiq_model_psi_score > 0.25",
        duration="5m",
        severity=AlertSeverity.WARNING,
        summary="Significant Population Stability Index (PSI) drift on active ML model",
        description="Model PSI score exceeds 0.25 threshold, triggering automated canary retraining pipeline.",
    ),
]


class EnterpriseObservabilityEngine:
    """Master Observability and APM Engine unifying Prometheus, Loki, and Grafana."""

    @classmethod
    def get_overview(cls) -> ObservabilityOverview:
        now_str = datetime.now(timezone.utc).isoformat()
        metrics = PrometheusMetricsRegistry.get_metrics()
        return ObservabilityOverview(
            apm_status="ONLINE_PROMETHEUS_LOKI_GRAFANA",
            total_metrics_tracked=len(metrics),
            scrape_interval_seconds=15,
            active_alerts_count=0,
            metrics=metrics,
            alert_rules=ALERT_RULES,
            timestamp=now_str,
        )

    @classmethod
    def get_alert_rules(cls) -> List[AlertRuleDefinition]:
        return ALERT_RULES

    @classmethod
    def get_logs(cls, limit: int = 50) -> List[LogStreamEntry]:
        return StructuredEnterpriseLogger.get_recent_logs(limit)
