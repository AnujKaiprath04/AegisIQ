from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.monitoring_logging import (
    AlertRuleDefinitionSchema,
    AlertRulesResponse,
    LogStreamEntrySchema,
    LogStreamResponse,
    ObservabilityOverviewResponse,
    ObservabilityOverviewSchema,
)
from app.monitoring_logging.engine import EnterpriseObservabilityEngine

router = APIRouter(prefix="/ops/observability", tags=["Part 4 - Module 6: Monitoring & Logging"])


@router.get("/overview", response_model=ObservabilityOverviewResponse)
def get_observability_overview(
    current_user: User = Depends(get_current_user),
):
    """Retrieve full observability stack overview, scrape metrics, and telemetry status."""
    overview = EnterpriseObservabilityEngine.get_overview()
    return ObservabilityOverviewResponse(overview=ObservabilityOverviewSchema(**overview.model_dump()))


@router.get("/alerts", response_model=AlertRulesResponse)
def get_alert_rules(
    current_user: User = Depends(get_current_user),
):
    """List configured Prometheus & Alertmanager alert rules, expression thresholds, and severity ratings."""
    rules = EnterpriseObservabilityEngine.get_alert_rules()
    return AlertRulesResponse(
        total_rules=len(rules),
        rules=[AlertRuleDefinitionSchema(**r.model_dump()) for r in rules],
    )


@router.get("/logs", response_model=LogStreamResponse)
def get_recent_logs(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Stream recent structured JSON application logs with trace correlation IDs."""
    logs = EnterpriseObservabilityEngine.get_logs(limit=limit)
    return LogStreamResponse(
        total_logs=len(logs),
        logs=[LogStreamEntrySchema(**entry.model_dump()) for entry in logs],
    )
