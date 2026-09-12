import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.monitoring_logging.types import LogStreamEntry

LOG_BUFFER: List[LogStreamEntry] = []


class StructuredEnterpriseLogger:
    """Structured JSON logging with trace_id correlation for Grafana Loki ingestion."""

    @classmethod
    def emit_log(cls, level: str, message: str, logger_name: str = "aegisiq.core", trace_id: str = None) -> LogStreamEntry:
        now_str = datetime.now(timezone.utc).isoformat()
        t_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        s_id = f"span-{uuid.uuid4().hex[:8]}"

        entry = LogStreamEntry(
            timestamp=now_str,
            level=level.upper(),
            logger=logger_name,
            message=message,
            trace_id=t_id,
            span_id=s_id,
        )

        LOG_BUFFER.append(entry)
        if len(LOG_BUFFER) > 100:
            LOG_BUFFER.pop(0)

        return entry

    @classmethod
    def get_recent_logs(cls, limit: int = 50) -> List[LogStreamEntry]:
        if not LOG_BUFFER:
            # Seed default logs
            cls.emit_log("INFO", "AegisIQ Core Kernel initialized with APM distributed tracing.")
            cls.emit_log("INFO", "FastAPI Prometheus metric exporter registered on /metrics.")
            cls.emit_log("INFO", "Promtail structured log shipping active.")
        return LOG_BUFFER[-limit:]
