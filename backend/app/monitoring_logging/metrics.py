from typing import List
from app.monitoring_logging.types import PrometheusMetricDefinition

STANDARD_METRICS: List[PrometheusMetricDefinition] = [
    PrometheusMetricDefinition(
        name="http_requests_total",
        metric_type="counter",
        description="Total number of HTTP requests processed by status and path",
        current_value=142850.0,
    ),
    PrometheusMetricDefinition(
        name="http_request_duration_seconds",
        metric_type="histogram",
        description="HTTP request latency distributions across endpoints (P50: 18ms, P90: 45ms, P99: 110ms)",
        current_value=0.018,
    ),
    PrometheusMetricDefinition(
        name="pg_stat_activity_count",
        metric_type="gauge",
        description="Active connected database client sessions in connection pool",
        current_value=14.0,
    ),
    PrometheusMetricDefinition(
        name="aegisiq_ml_inference_seconds",
        metric_type="histogram",
        description="Model inference execution latency across 7 predictive models",
        current_value=0.034,
    ),
    PrometheusMetricDefinition(
        name="aegisiq_model_psi_score",
        metric_type="gauge",
        description="Population Stability Index (PSI) drift metric across production models",
        current_value=0.042,
    ),
]


class PrometheusMetricsRegistry:
    """Manages custom Prometheus metric definitions."""

    @classmethod
    def get_metrics(cls) -> List[PrometheusMetricDefinition]:
        return STANDARD_METRICS
