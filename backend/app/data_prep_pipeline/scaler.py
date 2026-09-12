import math
from typing import Any, Dict, List, Optional, Tuple
from app.data_prep_pipeline.types import ScalingMethod


class FeatureScaler:
    """Performs numerical feature scaling (Standard, MinMax, Robust)."""

    @classmethod
    def fit_transform(
        cls,
        records: List[Dict[str, Any]],
        method: ScalingMethod = ScalingMethod.STANDARD,
        exclude_columns: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not records or method == ScalingMethod.NONE:
            return records, {}

        exclude = set(exclude_columns or [])
        cols = list(records[0].keys())
        params: Dict[str, Any] = {}

        # 1. Compute scaling parameters for numeric features
        for c in cols:
            if c in exclude:
                continue

            vals = [float(r[c]) for r in records if isinstance(r.get(c), (int, float)) and not isinstance(r.get(c), bool)]
            if len(vals) < len(records):
                continue  # Non-numeric column

            n = len(vals)
            if method == ScalingMethod.STANDARD:
                mean = sum(vals) / n
                variance = sum((x - mean) ** 2 for x in vals) / max(1, n - 1)
                std = math.sqrt(variance) or 1.0
                params[c] = {"method": "STANDARD", "mean": mean, "std": std}

            elif method == ScalingMethod.MINMAX:
                min_v = min(vals)
                max_v = max(vals)
                range_v = (max_v - min_v) or 1.0
                params[c] = {"method": "MINMAX", "min": min_v, "max": max_v, "range": range_v}

            elif method == ScalingMethod.ROBUST:
                sorted_v = sorted(vals)
                q1 = sorted_v[int(0.25 * n)]
                q2 = sorted_v[int(0.50 * n)]
                q3 = sorted_v[int(0.75 * n)]
                iqr = (q3 - q1) or 1.0
                params[c] = {"method": "ROBUST", "median": q2, "iqr": iqr}

        # 2. Transform records
        scaled_records = []
        for r in records:
            new_r = dict(r)
            for c, p in params.items():
                val = float(new_r[c])
                if p["method"] == "STANDARD":
                    new_r[c] = round((val - p["mean"]) / p["std"], 4)
                elif p["method"] == "MINMAX":
                    new_r[c] = round((val - p["min"]) / p["range"], 4)
                elif p["method"] == "ROBUST":
                    new_r[c] = round((val - p["median"]) / p["iqr"], 4)
            scaled_records.append(new_r)

        return scaled_records, params
