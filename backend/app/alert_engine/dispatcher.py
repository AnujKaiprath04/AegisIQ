from typing import Any, Dict, List
from app.alert_engine.types import AlertChannel, AlertSeverity


class MultiChannelDispatcher:
    """Formats and dispatches notifications across enterprise communication backends."""

    @classmethod
    def format_slack_payload(
        cls,
        title: str,
        description: str,
        severity: AlertSeverity,
        entity: str,
    ) -> Dict[str, Any]:
        emoji = "🚨" if severity == AlertSeverity.CRITICAL else "⚠️" if severity == AlertSeverity.HIGH else "ℹ️"
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"{emoji} AegisIQ Alert: {title}"},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:* `{severity.value}`"},
                        {"type": "mrkdwn", "text": f"*Target Entity:* `{entity}`"},
                    ],
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": description},
                },
            ]
        }

    @classmethod
    def format_teams_payload(
        cls,
        title: str,
        description: str,
        severity: AlertSeverity,
        entity: str,
    ) -> Dict[str, Any]:
        theme_color = "EA4335" if severity == AlertSeverity.CRITICAL else "FBBC04"
        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": title,
            "sections": [
                {
                    "activityTitle": f"AegisIQ Alert: {title}",
                    "activitySubtitle": f"Severity: {severity.value} | Entity: {entity}",
                    "text": description,
                }
            ],
        }

    @classmethod
    def format_webhook_payload(
        cls,
        incident_id: str,
        title: str,
        description: str,
        severity: AlertSeverity,
        entity: str,
    ) -> Dict[str, Any]:
        return {
            "platform": "AegisIQ Enterprise Intelligence",
            "incident_id": incident_id,
            "title": title,
            "description": description,
            "severity": severity.value,
            "target_entity": entity,
        }
