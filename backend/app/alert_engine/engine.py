import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.alert_engine.types import (
    AlertChannel,
    AlertIncident,
    AlertRule,
    AlertSeverity,
    AlertStatus,
    AlertTriggerSource,
)
from app.alert_engine.dispatcher import MultiChannelDispatcher
from app.alert_engine.deduplicator import AlertDeduplicationEngine

SEEDED_ALERT_RULES: List[AlertRule] = [
    AlertRule(
        rule_id="RULE-CHURN-001",
        name="Critical Customer Churn Risk Trigger",
        trigger_source=AlertTriggerSource.PREDICTION_CHURN,
        condition_metric="churn_probability",
        threshold=0.70,
        target_channels=[AlertChannel.SLACK, AlertChannel.IN_APP, AlertChannel.EMAIL],
        escalation_enabled=True,
        dedup_window_minutes=15,
        is_active=True,
    ),
    AlertRule(
        rule_id="RULE-SEC-002",
        name="Critical SIEM Threat Ingress Alert",
        trigger_source=AlertTriggerSource.CYBERSECURITY_SIEM,
        condition_metric="anomaly_score",
        threshold=0.90,
        target_channels=[AlertChannel.SLACK, AlertChannel.MICROSOFT_TEAMS, AlertChannel.WEBHOOK],
        escalation_enabled=True,
        dedup_window_minutes=10,
        is_active=True,
    ),
    AlertRule(
        rule_id="RULE-ANOM-003",
        name="Statistical 5-Sigma Anomaly Outlier Alert",
        trigger_source=AlertTriggerSource.ANOMALY_OUTLIER,
        condition_metric="z_score",
        threshold=3.5,
        target_channels=[AlertChannel.WEBHOOK, AlertChannel.IN_APP],
        escalation_enabled=False,
        dedup_window_minutes=5,
        is_active=True,
    ),
    AlertRule(
        rule_id="RULE-RISK-004",
        name="Elevated Business Risk Scorecard Trigger",
        trigger_source=AlertTriggerSource.BUSINESS_RISK,
        condition_metric="risk_score",
        threshold=35.0,
        target_channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
        escalation_enabled=True,
        dedup_window_minutes=30,
        is_active=True,
    ),
]

SEEDED_ALERT_INCIDENTS: List[AlertIncident] = [
    AlertIncident(
        incident_id="alert-inc-001",
        rule_id="RULE-CHURN-001",
        title="High Churn Danger: Apex Global Logistics",
        description="Predicted churn probability (74%) threatens $480k ARR.",
        severity=AlertSeverity.CRITICAL,
        trigger_source=AlertTriggerSource.PREDICTION_CHURN,
        status=AlertStatus.DISPATCHED,
        dispatched_channels=[AlertChannel.SLACK, AlertChannel.IN_APP, AlertChannel.EMAIL],
        target_entity="ACC-APEX-001",
        current_escalation_tier=1,
        triggered_at="2026-08-31T06:00:00Z",
    ),
    AlertIncident(
        incident_id="alert-inc-002",
        rule_id="RULE-SEC-002",
        title="Brute-Force Password Spraying Detected",
        description="48 failed logins in 60s from 198.51.100.44.",
        severity=AlertSeverity.CRITICAL,
        trigger_source=AlertTriggerSource.CYBERSECURITY_SIEM,
        status=AlertStatus.ACKNOWLEDGED,
        dispatched_channels=[AlertChannel.SLACK, AlertChannel.MICROSOFT_TEAMS, AlertChannel.WEBHOOK],
        target_entity="198.51.100.44",
        current_escalation_tier=1,
        triggered_at="2026-08-31T06:05:00Z",
        acknowledged_at="2026-08-31T06:07:00Z",
    ),
]


class EnterpriseAlertEngine:
    """Master Alert & Multi-Channel Notification Engine."""

    _rules: Dict[str, AlertRule] = {r.rule_id: r for r in SEEDED_ALERT_RULES}
    _incidents: Dict[str, AlertIncident] = {i.incident_id: i for i in SEEDED_ALERT_INCIDENTS}

    @classmethod
    def list_rules(cls) -> List[AlertRule]:
        return list(cls._rules.values())

    @classmethod
    def create_or_update_rule(cls, rule: AlertRule) -> AlertRule:
        cls._rules[rule.rule_id] = rule
        return rule

    @classmethod
    def list_incidents(
        cls,
        severity: Optional[AlertSeverity] = None,
        status_filter: Optional[AlertStatus] = None,
    ) -> List[AlertIncident]:
        incidents = list(cls._incidents.values())
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if status_filter:
            incidents = [i for i in incidents if i.status == status_filter]
        incidents.sort(key=lambda x: x.triggered_at, reverse=True)
        return incidents

    @classmethod
    def dispatch_alert(
        cls,
        rule_id: str,
        title: str,
        description: str,
        severity: AlertSeverity,
        target_entity: str,
        trigger_source: AlertTriggerSource,
        override_channels: Optional[List[AlertChannel]] = None,
    ) -> AlertIncident:
        rule = cls._rules.get(rule_id)
        window = rule.dedup_window_minutes if rule else 15

        # Check deduplication
        is_dup = AlertDeduplicationEngine.is_duplicate(rule_id, target_entity, severity.value, window)
        now_str = datetime.now(timezone.utc).isoformat()
        inc_id = f"alert-inc-{int(time.time())}"

        if is_dup:
            return AlertIncident(
                incident_id=inc_id,
                rule_id=rule_id,
                title=title,
                description=f"[SUPPRESSED DUPLICATE] {description}",
                severity=severity,
                trigger_source=trigger_source,
                status=AlertStatus.SUPPRESSED_DUPLICATE,
                dispatched_channels=[],
                target_entity=target_entity,
                triggered_at=now_str,
            )

        channels = override_channels or (rule.target_channels if rule else [AlertChannel.SLACK, AlertChannel.IN_APP])

        # Format multi-channel payloads
        payloads: Dict[str, Any] = {
            "slack": MultiChannelDispatcher.format_slack_payload(title, description, severity, target_entity),
            "teams": MultiChannelDispatcher.format_teams_payload(title, description, severity, target_entity),
            "webhook": MultiChannelDispatcher.format_webhook_payload(inc_id, title, description, severity, target_entity),
        }

        incident = AlertIncident(
            incident_id=inc_id,
            rule_id=rule_id,
            title=title,
            description=description,
            severity=severity,
            trigger_source=trigger_source,
            status=AlertStatus.DISPATCHED,
            dispatched_channels=channels,
            target_entity=target_entity,
            channel_payloads=payloads,
            triggered_at=now_str,
        )

        cls._incidents[inc_id] = incident
        return incident

    @classmethod
    def acknowledge_incident(cls, incident_id: str) -> AlertIncident:
        inc = cls._incidents.get(incident_id)
        if not inc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")

        inc.status = AlertStatus.ACKNOWLEDGED
        inc.acknowledged_at = datetime.now(timezone.utc).isoformat()
        return inc

    @classmethod
    def resolve_incident(cls, incident_id: str) -> AlertIncident:
        inc = cls._incidents.get(incident_id)
        if not inc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found.")

        inc.status = AlertStatus.RESOLVED
        inc.resolved_at = datetime.now(timezone.utc).isoformat()
        return inc
