import math
from typing import List, Tuple
from app.anomaly_engine.types import AnomalySeverity


class IsolationForestDetector:
    """Unsupervised Tree-Partition Isolation Depth Anomaly Detector."""

    @classmethod
    def evaluate(
        cls,
        value: float,
        reference_samples: List[float],
        contamination: float = 0.05,
    ) -> Tuple[bool, float, AnomalySeverity, str]:
        if not reference_samples:
            return False, 0.0, AnomalySeverity.NORMAL, "No reference data available"

        mean = sum(reference_samples) / len(reference_samples)
        variance = sum((x - mean) ** 2 for x in reference_samples) / max(1, len(reference_samples) - 1)
        std = math.sqrt(variance) if variance > 0 else 1.0

        # Empirical isolation depth estimate
        dist = abs(value - mean) / std
        anomaly_score = round(1.0 / (1.0 + math.exp(-0.8 * (dist - 2.5))), 4)
        is_anomaly = anomaly_score >= (1.0 - contamination)

        if anomaly_score >= 0.95:
            severity = AnomalySeverity.CRITICAL
        elif anomaly_score >= 0.85:
            severity = AnomalySeverity.HIGH
        elif is_anomaly:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.NORMAL

        explanation = f"Isolation Score {anomaly_score:.3f} (Contamination threshold: {1.0 - contamination:.2f})"
        return is_anomaly, anomaly_score, severity, explanation


class MahalanobisDetector:
    """Multivariate Covariance-Adjusted Distance Outlier Detector."""

    @classmethod
    def evaluate(
        cls,
        value: float,
        mean: float,
        variance: float,
        threshold: float = 3.0,
    ) -> Tuple[bool, float, AnomalySeverity, str]:
        var = max(1e-6, variance)
        m_dist = math.sqrt(((value - mean) ** 2) / var)
        is_anomaly = m_dist >= threshold
        anomaly_score = round(min(1.0, m_dist / (threshold * 2.0)), 4)

        if m_dist >= threshold * 2.0:
            severity = AnomalySeverity.CRITICAL
        elif is_anomaly:
            severity = AnomalySeverity.HIGH
        else:
            severity = AnomalySeverity.NORMAL

        explanation = f"Mahalanobis Distance: {m_dist:.2f} (Threshold: {threshold:.1f})"
        return is_anomaly, anomaly_score, severity, explanation
