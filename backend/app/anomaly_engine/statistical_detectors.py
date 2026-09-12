import math
from typing import List, Tuple
from app.anomaly_engine.types import AnomalySeverity


class ZScoreDetector:
    """Parametric Z-Score Standard Normal Distribution Outlier Detector."""

    @classmethod
    def evaluate(
        cls,
        value: float,
        mean: float,
        std: float,
        z_threshold: float = 3.0,
    ) -> Tuple[bool, float, AnomalySeverity, str]:
        if std <= 0:
            std = 1e-6

        z_val = abs(value - mean) / std
        is_anomaly = z_val >= z_threshold
        anomaly_score = round(min(1.0, z_val / (z_threshold * 2.0)), 4)

        if z_val >= z_threshold * 2.0:
            severity = AnomalySeverity.CRITICAL
        elif z_val >= z_threshold * 1.5:
            severity = AnomalySeverity.HIGH
        elif z_val >= z_threshold:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.NORMAL

        explanation = f"Z-Score {z_val:.2f} (Threshold: {z_threshold:.1f}, Mean: {mean:.2f}, Std: {std:.2f})"
        return is_anomaly, anomaly_score, severity, explanation


class IQRDetector:
    """Non-Parametric Interquartile Range (IQR) Dispersion Fencing Detector."""

    @classmethod
    def evaluate(
        cls,
        value: float,
        q1: float,
        q3: float,
        multiplier: float = 1.5,
    ) -> Tuple[bool, float, AnomalySeverity, str]:
        iqr = max(1e-6, q3 - q1)
        lower_fence = q1 - (multiplier * iqr)
        upper_fence = q3 + (multiplier * iqr)

        is_anomaly = value < lower_fence or value > upper_fence

        if value < lower_fence:
            diff = lower_fence - value
        elif value > upper_fence:
            diff = value - upper_fence
        else:
            diff = 0.0

        anomaly_score = round(min(1.0, diff / (iqr * 2.0)), 4)

        if diff >= iqr * 2.0:
            severity = AnomalySeverity.CRITICAL
        elif diff >= iqr:
            severity = AnomalySeverity.HIGH
        elif diff > 0:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.NORMAL

        explanation = f"IQR Fence [{lower_fence:.2f}, {upper_fence:.2f}], Diff: {diff:.2f}"
        return is_anomaly, anomaly_score, severity, explanation
