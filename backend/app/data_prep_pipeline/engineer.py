import re
from datetime import datetime
from typing import Any, Dict, List, Tuple


class FeatureEngineer:
    """Extracts temporal features from timestamps and computes feature interactions."""

    ISO_DATE_REGEX = r"^\d{4}-\d{2}-\d{2}"

    @classmethod
    def is_iso_date(cls, val: Any) -> bool:
        if isinstance(val, str) and re.match(cls_pattern := cls.ISO_DATE_REGEX, val.strip()):
            return True
        return False

    @classmethod
    def engineer_features(
        cls,
        records: List[Dict[str, Any]],
        extract_datetimes: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not records or not extract_datetimes:
            return records, {}

        cols = list(records[0].keys())
        date_cols = []

        # Find datetime columns
        for c in cols:
            first_valid = next((r[c] for r in records if r.get(c) is not None), None)
            if cls.is_iso_date(first_valid):
                date_cols.append(c)

        engineered_records = []
        for r in records:
            new_r = dict(r)
            for dc in date_cols:
                val_str = str(new_r.get(dc, "")).replace("Z", "").split(".")[0]
                try:
                    dt = datetime.fromisoformat(val_str)
                    new_r[f"{dc}_year"] = dt.year
                    new_r[f"{dc}_month"] = dt.month
                    new_r[f"{dc}_day"] = dt.day
                    new_r[f"{dc}_day_of_week"] = dt.weekday()
                    new_r[f"{dc}_is_weekend"] = 1.0 if dt.weekday() >= 5 else 0.0
                    new_r[f"{dc}_quarter"] = (dt.month - 1) // 3 + 1
                    # Remove original raw timestamp string to make dataset ML-ready
                    del new_r[dc]
                except Exception:
                    pass
            engineered_records.append(new_r)

        metadata = {
            "datetime_columns_expanded": date_cols,
            "features_created_count": len(date_cols) * 6,
        }
        return engineered_records, metadata
