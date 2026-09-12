from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.monitoring_logging.types import (
    AlertRuleDefinition,
    LogStreamEntry,
    ObservabilityOverview,
    PrometheusMetricDefinition,
)


class PrometheusMetricDefinitionSchema(PrometheusMetricDefinition):
    pass


class AlertRuleDefinitionSchema(AlertRuleDefinition):
    pass


class LogStreamEntrySchema(LogStreamEntry):
    pass


class ObservabilityOverviewSchema(ObservabilityOverview):
    pass


class ObservabilityOverviewResponse(BaseModel):
    overview: ObservabilityOverviewSchema


class AlertRulesResponse(BaseModel):
    total_rules: int
    rules: List[AlertRuleDefinitionSchema] = []


class LogStreamResponse(BaseModel):
    total_logs: int
    logs: List[LogStreamEntrySchema] = []
