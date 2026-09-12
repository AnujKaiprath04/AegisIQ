import math
from collections import Counter
from typing import Any, Dict, List, Tuple
from app.data_prep_pipeline.types import ImputationStrategy


class MissingValueImputer:
    """Handles numerical and categorical missing value imputation."""

    @classmethod
    def is_null(cls, val: Any) -> bool:
        if val is None or val == "":
            return True
        if isinstance(val, float) and math.isnan(val):
            return True
        return False

    @classmethod
    def impute(
        cls,
        records: List[Dict[str, Any]],
        num_strategy: ImputationStrategy = ImputationStrategy.MEAN,
        cat_strategy: ImputationStrategy = ImputationStrategy.MODE,
        fill_constant_num: float = 0.0,
        fill_constant_cat: str = "UNKNOWN",
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not records:
            return [], {}

        # 1. Identify columns and non-null values
        cols = list(records[0].keys())
        stats: Dict[str, Any] = {}

        for c in cols:
            valid_vals = [r[c] for r in records if not cls.is_null(r.get(c))]
            if not valid_vals:
                stats[c] = {"type": "empty", "fill": fill_constant_cat}
                continue

            first_val = valid_vals[0]
            if isinstance(first_val, (int, float)) and not isinstance(first_val, bool):
                # Numerical
                if num_strategy == ImputationStrategy.MEAN:
                    mean_val = sum(valid_vals) / len(valid_vals)
                    stats[c] = {"type": "numeric", "fill": round(mean_val, 4)}
                elif num_strategy == ImputationStrategy.MEDIAN:
                    sorted_v = sorted(valid_vals)
                    med_val = sorted_v[len(sorted_v) // 2]
                    stats[c] = {"type": "numeric", "fill": med_val}
                else:
                    stats[c] = {"type": "numeric", "fill": fill_constant_num}
            else:
                # Categorical
                if cat_strategy == ImputationStrategy.MODE:
                    mode_val = Counter(valid_vals).most_common(1)[0][0]
                    stats[c] = {"type": "categorical", "fill": mode_val}
                else:
                    stats[c] = {"type": "categorical", "fill": fill_constant_cat}

        # 2. Impute records
        imputed_records = []
        for r in records:
            new_r = dict(r)
            for c in cols:
                if cls.is_null(new_r.get(c)):
                    new_r[c] = stats[c]["fill"]
            imputed_records.append(new_r)

        return imputed_records, stats
