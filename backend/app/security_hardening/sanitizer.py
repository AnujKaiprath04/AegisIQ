import html
import re
from datetime import datetime, timezone
from typing import Optional

from app.security_hardening.types import (
    ThreatCategory,
    ThreatInspectionRequest,
    ThreatInspectionResult,
)

SQLI_PATTERN = re.compile(r"(\bUNION\b\s+\bSELECT\b|--|;\s*DROP\b|\bOR\b\s+1\s*=\s*1|'\s*OR\s*'1'\s*=\s*'1')", re.IGNORECASE)
XSS_PATTERN = re.compile(r"(<script[\s\S]*?>[\s\S]*?<\/script>|javascript:|onerror\s*=|onload\s*=|alert\(|<iframe)", re.IGNORECASE)
TRAVERSAL_PATTERN = re.compile(r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e\/)", re.IGNORECASE)
COMMAND_PATTERN = re.compile(r"(;\s*rm\s+-rf|;\s*cat\s+\/etc\/passwd|\|\s*bash|`.*`)", re.IGNORECASE)


class EnterpriseInputSanitizer:
    """Deep input sanitization and multi-vector threat detector."""

    @classmethod
    def inspect_and_sanitize(cls, req: ThreatInspectionRequest) -> ThreatInspectionResult:
        now_str = datetime.now(timezone.utc).isoformat()
        raw = req.payload

        # 1. Check SQLi
        sqli_match = SQLI_PATTERN.search(raw)
        if sqli_match:
            sanitized = SQLI_PATTERN.sub("[REDACTED_SQLI_ATTEMPT]", raw)
            return ThreatInspectionResult(
                is_threat_detected=True,
                detected_category=ThreatCategory.SQL_INJECTION,
                matched_pattern=sqli_match.group(0),
                sanitized_output=sanitized,
                risk_level="CRITICAL",
                inspection_timestamp=now_str,
            )

        # 2. Check XSS
        xss_match = XSS_PATTERN.search(raw)
        if xss_match:
            sanitized = html.escape(raw)
            return ThreatInspectionResult(
                is_threat_detected=True,
                detected_category=ThreatCategory.CROSS_SITE_SCRIPTING,
                matched_pattern=xss_match.group(0),
                sanitized_output=sanitized,
                risk_level="HIGH",
                inspection_timestamp=now_str,
            )

        # 3. Check Traversal
        trav_match = TRAVERSAL_PATTERN.search(raw)
        if trav_match:
            sanitized = TRAVERSAL_PATTERN.sub("", raw)
            return ThreatInspectionResult(
                is_threat_detected=True,
                detected_category=ThreatCategory.PATH_TRAVERSAL,
                matched_pattern=trav_match.group(0),
                sanitized_output=sanitized,
                risk_level="HIGH",
                inspection_timestamp=now_str,
            )

        # 4. Check Command Injection
        cmd_match = COMMAND_PATTERN.search(raw)
        if cmd_match:
            sanitized = COMMAND_PATTERN.sub("[REDACTED_CMD_ATTEMPT]", raw)
            return ThreatInspectionResult(
                is_threat_detected=True,
                detected_category=ThreatCategory.COMMAND_INJECTION,
                matched_pattern=cmd_match.group(0),
                sanitized_output=sanitized,
                risk_level="CRITICAL",
                inspection_timestamp=now_str,
            )

        # Benign clean output
        return ThreatInspectionResult(
            is_threat_detected=False,
            detected_category=ThreatCategory.BENIGN,
            matched_pattern=None,
            sanitized_output=raw,
            risk_level="NONE_BENIGN",
            inspection_timestamp=now_str,
        )
