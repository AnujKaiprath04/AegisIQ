from typing import Any, Dict, List, Optional, Tuple
from app.data_prep_pipeline.types import EncodingMethod


class CategoricalEncoder:
    """Encodes categorical string features using One-Hot or Ordinal encoding."""

    @classmethod
    def fit_transform(
        cls,
        records: List[Dict[str, Any]],
        method: EncodingMethod = EncodingMethod.ONE_HOT,
        exclude_columns: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not records or method == EncodingMethod.NONE:
            return records, {}

        exclude = set(exclude_columns or [])
        cols = list(records[0].keys())
        vocabularies: Dict[str, Any] = {}

        # 1. Identify categorical columns
        cat_cols = []
        for c in cols:
            if c in exclude:
                continue
            vals = [r.get(c) for r in records if r.get(c) is not None]
            if any(isinstance(v, str) for v in vals):
                cat_cols.append(c)
                unique_vals = sorted(list({str(v) for v in vals}))
                vocabularies[c] = {"method": method.value, "categories": unique_vals}

        # 2. Transform records
        encoded_records = []
        for r in records:
            new_r = {}
            for c, val in r.items():
                if c not in cat_cols:
                    new_r[c] = val
                else:
                    val_str = str(val)
                    if method == EncodingMethod.ONE_HOT:
                        for cat in vocabularies[c]["categories"]:
                            clean_col = f"{c}_{cat.lower().replace(' ', '_').replace('-', '_')}"
                            new_r[clean_col] = 1.0 if val_str == cat else 0.0
                    elif method == EncodingMethod.ORDINAL:
                        cats = vocabularies[c]["categories"]
                        idx = cats.index(val_str) if val_str in cats else 0
                        new_r[c] = idx
            encoded_records.append(new_r)

        return encoded_records, vocabularies
