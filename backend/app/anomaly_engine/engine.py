import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.anomaly_engine.types import (
    AnomalyDomain,
    AnomalyMethod,
    AnomalyPoint,
    AnomalySeverity,
    BatchAnomalyResult,
    DomainProfile,
)
from app.anomaly_engine.statistical_detectors import IQRDetector, ZScoreDetector
from app.anomaly_engine.ml_detectors import IsolationForestDetector, MahalanobisDetector

DOMAIN_PROFILES: Dict[AnomalyDomain, DomainProfile] = {
    AnomalyDomain.FINANCIAL: DomainProfile(
        domain=AnomalyDomain.FINANCIAL,
        metric_name="Transaction Amount USD",
        baseline_mean=2450.0,
        baseline_std=480.0,
        iqr_lower=1200.0,
        iqr_upper=3800.0,
        threshold=3.0,
    ),
    AnomalyDomain.SYSTEM_TELEMETRY: DomainProfile(
        domain=AnomalyDomain.SYSTEM_TELEMETRY,
        metric_name="CPU Utilization %",
        baseline_mean=42.5,
        baseline_std=12.8,
        iqr_lower=25.0,
        iqr_upper=65.0,
        threshold=3.0,
    ),
    AnomalyDomain.USER_BEHAVIOR: DomainProfile(
        domain=AnomalyDomain.USER_BEHAVIOR,
        metric_name="Queries Per Minute",
        baseline_mean=35.0,
        baseline_std=10.5,
        iqr_lower=18.0,
        iqr_upper=55.0,
        threshold=3.0,
    ),
    AnomalyDomain.REVENUE: DomainProfile(
        domain=AnomalyDomain.REVENUE,
        metric_name="Intraday Order Velocity",
        baseline_mean=185.0,
        baseline_std=32.0,
        iqr_lower=120.0,
        iqr_upper=240.0,
        threshold=3.0,
    ),
}

SEEDED_RECENT_ANOMALIES: List[AnomalyPoint] = [
    AnomalyPoint(
        timestamp="2026-08-31T06:12:00Z",
        value=18500.0,
        is_anomaly=True,
        anomaly_score=0.98,
        severity=AnomalySeverity.CRITICAL,
        method_used=AnomalyMethod.Z_SCORE,
        expected_range=[1200.0, 3800.0],
        explanation="Z-Score 33.44: Transaction Amount ($18,500.00) breached upper threshold ($3,890.00)",
    ),
    AnomalyPoint(
        timestamp="2026-08-31T06:45:00Z",
        value=98.4,
        is_anomaly=True,
        anomaly_score=0.94,
        severity=AnomalySeverity.HIGH,
        method_used=AnomalyMethod.ISOLATION_FOREST,
        expected_range=[25.0, 65.0],
        explanation="Isolation Score 0.962: CPU Utilization (98.4%) exceeded multi-dimensional cluster baseline",
    ),
    AnomalyPoint(
        timestamp="2026-08-31T07:10:00Z",
        value=240.0,
        is_anomaly=True,
        anomaly_score=0.88,
        severity=AnomalySeverity.MEDIUM,
        method_used=AnomalyMethod.IQR,
        expected_range=[18.0, 55.0],
        explanation="IQR Fence Exceeded: Queries Per Minute (240 QPM) exceeded upper fence (110.5 QPM)",
    ),
]


class EnterpriseAnomalyEngine:
    """Master Streaming and Batch Anomaly Detection Engine."""

    _recent_anomalies: List[AnomalyPoint] = list(SEEDED_RECENT_ANOMALIES)

    @classmethod
    def detect_stream(
        cls,
        domain: AnomalyDomain,
        value: float,
        method: AnomalyMethod = AnomalyMethod.ENSEMBLE,
    ) -> AnomalyPoint:
        profile = DOMAIN_PROFILES.get(domain, DOMAIN_PROFILES[AnomalyDomain.SYSTEM_TELEMETRY])
        now_str = datetime.now(timezone.utc).isoformat()

        if method == AnomalyMethod.Z_SCORE:
            is_anom, score, sev, expl = ZScoreDetector.evaluate(value, profile.baseline_mean, profile.baseline_std, profile.threshold)
        elif method == AnomalyMethod.IQR:
            is_anom, score, sev, expl = IQRDetector.evaluate(value, profile.iqr_lower, profile.iqr_upper)
        elif method == AnomalyMethod.ISOLATION_FOREST:
            ref = [profile.baseline_mean - profile.baseline_std, profile.baseline_mean, profile.baseline_mean + profile.baseline_std]
            is_anom, score, sev, expl = IsolationForestDetector.evaluate(value, ref)
        elif method == AnomalyMethod.MAHALANOBIS:
            is_anom, score, sev, expl = MahalanobisDetector.evaluate(value, profile.baseline_mean, profile.baseline_std ** 2)
        else:  # ENSEMBLE
            z_anom, z_score, z_sev, z_expl = ZScoreDetector.evaluate(value, profile.baseline_mean, profile.baseline_std)
            iqr_anom, iqr_score, iqr_sev, iqr_expl = IQRDetector.evaluate(value, profile.iqr_lower, profile.iqr_upper)
            is_anom = z_anom or iqr_anom
            score = round((z_score + iqr_score) / 2.0, 4)
            sev = z_sev if z_anom else iqr_sev
            expl = f"Ensemble: {z_expl} | {iqr_expl}"

        point = AnomalyPoint(
            timestamp=now_str,
            value=value,
            is_anomaly=is_anom,
            anomaly_score=score,
            severity=sev,
            method_used=method,
            expected_range=[profile.iqr_lower, profile.iqr_upper],
            explanation=expl,
        )

        if is_anom:
            cls._recent_anomalies.insert(0, point)
            if len(cls._recent_anomalies) > 50:
                cls._recent_anomalies.pop()

        return point

    @classmethod
    def detect_batch(
        cls,
        values: List[float],
        method: AnomalyMethod = AnomalyMethod.Z_SCORE,
        threshold: float = 3.0,
    ) -> BatchAnomalyResult:
        start_t = time.time()
        if not values:
            return BatchAnomalyResult(
                total_records=0,
                anomaly_count=0,
                anomaly_percentage=0.0,
                method_used=method,
                anomalies=[],
                execution_time_ms=0.0,
            )

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / max(1, len(values) - 1)
        std = math_sqrt = variance ** 0.5 if variance > 0 else 1.0

        anomalies: List[AnomalyPoint] = []
        now_str = datetime.now(timezone.utc).isoformat()

        for idx, val in enumerate(values):
            is_anom, score, sev, expl = ZScoreDetector.evaluate(val, mean, std, threshold)
            if is_anom:
                anomalies.append(
                    AnomalyPoint(
                        timestamp=now_str,
                        value=val,
                        is_anomaly=True,
                        anomaly_score=score,
                        severity=sev,
                        method_used=method,
                        expected_range=[round(mean - (2 * std), 2), round(mean + (2 * std), 2)],
                        explanation=f"Index {idx}: {expl}",
                    )
                )

        exec_ms = round((time.time() - start_t) * 1000.0, 2)
        pct = round((len(anomalies) / len(values)) * 100.0, 2)

        return BatchAnomalyResult(
            total_records=len(values),
            anomaly_count=len(anomalies),
            anomaly_percentage=pct,
            method_used=method,
            anomalies=anomalies,
            execution_time_ms=exec_ms,
        )

    @classmethod
    def get_profiles(cls) -> List[DomainProfile]:
        return list(DOMAIN_PROFILES.values())

    @classmethod
    def get_recent_anomalies(cls) -> List[AnomalyPoint]:
        return cls._recent_anomalies
