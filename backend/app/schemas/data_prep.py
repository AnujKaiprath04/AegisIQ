from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.data_prep_pipeline.types import (
    PipelineConfig,
    PreprocessedDatasetResult,
    SplitMethod,
)


class DataPrepProcessRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., min_length=1)
    config: Optional[PipelineConfig] = None


class DataPrepProcessResponse(BaseModel):
    total_rows: int
    feature_names: List[str] = []
    target_column: Optional[str] = None
    train_count: int
    test_count: int
    val_count: int
    train_sample: List[Dict[str, Any]] = []
    test_sample: List[Dict[str, Any]] = []
    pipeline_metadata: Dict[str, Any] = {}


class DataSplitRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., min_length=3)
    train_ratio: float = 0.70
    test_ratio: float = 0.15
    val_ratio: float = 0.15
    target_column: Optional[str] = None
    method: SplitMethod = SplitMethod.RANDOM


class DataSplitResponse(BaseModel):
    total_rows: int
    train_count: int
    test_count: int
    val_count: int
    train_sample: List[Dict[str, Any]] = []
    test_sample: List[Dict[str, Any]] = []
    val_sample: List[Dict[str, Any]] = []


class FeatureEngineerRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., min_length=1)
    extract_datetimes: bool = True


class FeatureEngineerResponse(BaseModel):
    total_rows: int
    features_created_count: int
    engineered_sample: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class PresetListResponse(BaseModel):
    presets: List[Dict[str, Any]] = []
