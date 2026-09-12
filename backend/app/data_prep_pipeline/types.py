from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ImputationStrategy(str, Enum):
    MEAN = "MEAN"
    MEDIAN = "MEDIAN"
    MODE = "MODE"
    CONSTANT = "CONSTANT"
    DROP = "DROP"


class ScalingMethod(str, Enum):
    STANDARD = "STANDARD"
    MINMAX = "MINMAX"
    ROBUST = "ROBUST"
    NONE = "NONE"


class EncodingMethod(str, Enum):
    ONE_HOT = "ONE_HOT"
    ORDINAL = "ORDINAL"
    NONE = "NONE"


class SplitMethod(str, Enum):
    RANDOM = "RANDOM"
    STRATIFIED = "STRATIFIED"
    TIME_SERIES = "TIME_SERIES"


class PreprocessingPreset(str, Enum):
    CHURN_PREDICTION = "CHURN_PREDICTION"
    REVENUE_FORECAST = "REVENUE_FORECAST"
    SIEM_ANOMALY = "SIEM_ANOMALY"
    CUSTOM = "CUSTOM"


class PipelineConfig(BaseModel):
    target_column: Optional[str] = None
    numerical_imputation: ImputationStrategy = ImputationStrategy.MEAN
    categorical_imputation: ImputationStrategy = ImputationStrategy.MODE
    scaling: ScalingMethod = ScalingMethod.STANDARD
    encoding: EncodingMethod = EncodingMethod.ONE_HOT
    engineer_datetimes: bool = True
    train_ratio: float = Field(default=0.70, ge=0.1, le=0.9)
    test_ratio: float = Field(default=0.15, ge=0.05, le=0.5)
    val_ratio: float = Field(default=0.15, ge=0.0, le=0.5)
    split_method: SplitMethod = SplitMethod.RANDOM


class PreprocessedDatasetResult(BaseModel):
    total_rows: int
    feature_names: List[str] = []
    target_column: Optional[str] = None
    train_count: int
    test_count: int
    val_count: int
    train_sample: List[Dict[str, Any]] = []
    test_sample: List[Dict[str, Any]] = []
    pipeline_metadata: Dict[str, Any] = {}
