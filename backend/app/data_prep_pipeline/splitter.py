import random
from typing import Any, Dict, List, Optional, Tuple
from app.data_prep_pipeline.types import SplitMethod


class DatasetSplitter:
    """Partitions datasets into Train, Test, and Validation sets (Random, Stratified, TimeSeries)."""

    @classmethod
    def split(
        cls,
        records: List[Dict[str, Any]],
        train_ratio: float = 0.70,
        test_ratio: float = 0.15,
        val_ratio: float = 0.15,
        target_column: Optional[str] = None,
        method: SplitMethod = SplitMethod.RANDOM,
        random_seed: int = 42,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not records:
            return [], [], []

        n = len(records)
        if n < 3:
            return records, [], []

        # Normalize ratios
        total = train_ratio + test_ratio + val_ratio
        tr_r = train_ratio / total
        te_r = test_ratio / total

        train_idx_count = max(1, int(n * tr_r))
        test_idx_count = max(1, int(n * te_r))

        if method == SplitMethod.TIME_SERIES:
            # Preserves chronological sequence
            train = records[:train_idx_count]
            test = records[train_idx_count : train_idx_count + test_idx_count]
            val = records[train_idx_count + test_idx_count :]
            return train, test, val

        elif method == SplitMethod.STRATIFIED and target_column and target_column in records[0]:
            # Stratified split by target classes
            groups: Dict[Any, List[Dict[str, Any]]] = {}
            for r in records:
                t_val = r.get(target_column)
                groups.setdefault(t_val, []).append(r)

            train, test, val = [], [], []
            for t_val, items in groups.items():
                random.Random(random_seed).shuffle(items)
                g_n = len(items)
                g_tr = max(1, int(g_n * tr_r))
                g_te = max(1, int(g_n * te_r)) if (g_n - g_tr) > 1 else 0
                train.extend(items[:g_tr])
                test.extend(items[g_tr : g_tr + g_te])
                val.extend(items[g_tr + g_te :])

            return train, test, val

        else:
            # Random split
            shuffled = list(records)
            random.Random(random_seed).shuffle(shuffled)
            train = shuffled[:train_idx_count]
            test = shuffled[train_idx_count : train_idx_count + test_idx_count]
            val = shuffled[train_idx_count + test_idx_count :]
            return train, test, val
