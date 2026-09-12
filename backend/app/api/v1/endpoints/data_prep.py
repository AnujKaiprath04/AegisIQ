from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.data_prep import (
    DataPrepProcessRequest,
    DataPrepProcessResponse,
    DataSplitRequest,
    DataSplitResponse,
    FeatureEngineerRequest,
    FeatureEngineerResponse,
    PresetListResponse,
)
from app.data_prep_pipeline.pipeline import DataPreparationPipeline
from app.data_prep_pipeline.splitter import DatasetSplitter
from app.data_prep_pipeline.engineer import FeatureEngineer
from app.data_prep_pipeline.types import PipelineConfig

router = APIRouter(prefix="/ml/data-prep", tags=["Part 3 - Module 2: Data Preparation Pipeline"])


@router.post("/process", response_model=DataPrepProcessResponse)
def process_dataset(
    req: DataPrepProcessRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute end-to-end data preparation pipeline (impute nulls, engineer features, encode, scale, and partition)."""
    cfg = req.config or PipelineConfig()
    result = DataPreparationPipeline.process(records=req.records, config=cfg)
    return DataPrepProcessResponse(**result.model_dump())


@router.post("/split", response_model=DataSplitResponse)
def split_dataset(
    req: DataSplitRequest,
    current_user: User = Depends(get_current_user),
):
    """Partition a dataset into Train, Test, and Validation partitions (Random, Stratified, TimeSeries)."""
    train, test, val = DatasetSplitter.split(
        records=req.records,
        train_ratio=req.train_ratio,
        test_ratio=req.test_ratio,
        val_ratio=req.val_ratio,
        target_column=req.target_column,
        method=req.method,
    )
    return DataSplitResponse(
        total_rows=len(req.records),
        train_count=len(train),
        test_count=len(test),
        val_count=len(val),
        train_sample=train[:5],
        test_sample=test[:5],
        val_sample=val[:5],
    )


@router.post("/engineer-features", response_model=FeatureEngineerResponse)
def engineer_features(
    req: FeatureEngineerRequest,
    current_user: User = Depends(get_current_user),
):
    """Extract temporal components (year, month, day, is_weekend, quarter) and interactions from raw data."""
    engineered, meta = FeatureEngineer.engineer_features(
        records=req.records,
        extract_datetimes=req.extract_datetimes,
    )
    return FeatureEngineerResponse(
        total_rows=len(req.records),
        features_created_count=meta.get("features_created_count", 0),
        engineered_sample=engineered[:5],
        metadata=meta,
    )


@router.get("/presets", response_model=PresetListResponse)
def list_presets(
    current_user: User = Depends(get_current_user),
):
    """List standard enterprise preprocessing presets (Churn Prediction, Revenue Forecast, SIEM Anomaly)."""
    presets = DataPreparationPipeline.list_presets()
    return PresetListResponse(presets=presets)
