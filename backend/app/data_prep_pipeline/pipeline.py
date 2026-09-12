import logging
from typing import Any, Dict, List, Optional
from app.data_prep_pipeline.types import (
    EncodingMethod,
    ImputationStrategy,
    PipelineConfig,
    PreprocessedDatasetResult,
    PreprocessingPreset,
    ScalingMethod,
    SplitMethod,
)
from app.data_prep_pipeline.imputer import MissingValueImputer
from app.data_prep_pipeline.scaler import FeatureScaler
from app.data_prep_pipeline.encoder import CategoricalEncoder
from app.data_prep_pipeline.engineer import FeatureEngineer
from app.data_prep_pipeline.splitter import DatasetSplitter

logger = logging.getLogger("aegisiq.data_prep_pipeline")


class DataPreparationPipeline:
    """Master Data Preparation and Feature Engineering Pipeline."""

    @classmethod
    def list_presets(cls) -> List[Dict[str, Any]]:
        return [
            {
                "preset": PreprocessingPreset.CHURN_PREDICTION.value,
                "title": "Customer Churn Prediction Preprocessing",
                "description": "Standard imputation, One-Hot categorical encoding, Standard scaling, and Stratified train/test split for churn classification.",
                "config": {
                    "target_column": "churn",
                    "numerical_imputation": "MEAN",
                    "categorical_imputation": "MODE",
                    "scaling": "STANDARD",
                    "encoding": "ONE_HOT",
                    "split_method": "STRATIFIED",
                },
            },
            {
                "preset": PreprocessingPreset.REVENUE_FORECAST.value,
                "title": "Time-Series Revenue & Sales Forecasting",
                "description": "Datetime component expansion (year, month, quarter), Robust scaling, and sequential TimeSeries train/test split.",
                "config": {
                    "target_column": "revenue",
                    "numerical_imputation": "MEDIAN",
                    "scaling": "ROBUST",
                    "engineer_datetimes": True,
                    "split_method": "TIME_SERIES",
                },
            },
            {
                "preset": PreprocessingPreset.SIEM_ANOMALY.value,
                "title": "Cybersecurity SIEM Ingress Anomaly Prep",
                "description": "MinMax normalization on network packet counters, categorical service encoding, and Unsupervised Random split.",
                "config": {
                    "numerical_imputation": "CONSTANT",
                    "scaling": "MINMAX",
                    "encoding": "ONE_HOT",
                    "split_method": "RANDOM",
                },
            },
        ]

    @classmethod
    def process(
        cls,
        records: List[Dict[str, Any]],
        config: PipelineConfig,
    ) -> PreprocessedDatasetResult:
        if not records:
            return PreprocessedDatasetResult(
                total_rows=0,
                feature_names=[],
                train_count=0,
                test_count=0,
                val_count=0,
            )

        metadata: Dict[str, Any] = {}

        # 1. Missing Value Imputation
        imputed_records, impute_meta = MissingValueImputer.impute(
            records=records,
            num_strategy=config.numerical_imputation,
            cat_strategy=config.categorical_imputation,
        )
        metadata["imputation"] = impute_meta

        # 2. Feature Engineering (Datetimes)
        engineered_records, eng_meta = FeatureEngineer.engineer_features(
            records=imputed_records,
            extract_datetimes=config.engineer_datetimes,
        )
        metadata["feature_engineering"] = eng_meta

        # 3. Categorical Encoding
        exclude_cols = [config.target_column] if config.target_column else []
        encoded_records, encode_meta = CategoricalEncoder.fit_transform(
            records=engineered_records,
            method=config.encoding,
            exclude_columns=exclude_cols,
        )
        metadata["encoding"] = encode_meta

        # 4. Feature Scaling
        scaled_records, scale_meta = FeatureScaler.fit_transform(
            records=encoded_records,
            method=config.scaling,
            exclude_columns=exclude_cols,
        )
        metadata["scaling"] = scale_meta

        # 5. Dataset Partitioning / Splitting
        train, test, val = DatasetSplitter.split(
            records=scaled_records,
            train_ratio=config.train_ratio,
            test_ratio=config.test_ratio,
            val_ratio=config.val_ratio,
            target_column=config.target_column,
            method=config.split_method,
        )

        all_features = list(scaled_records[0].keys()) if scaled_records else []
        feature_names = [f for f in all_features if f != config.target_column]

        logger.info(f"Processed {len(records)} records through DataPrep pipeline -> Train: {len(train)}, Test: {len(test)}, Val: {len(val)}")

        return PreprocessedDatasetResult(
            total_rows=len(records),
            feature_names=feature_names,
            target_column=config.target_column,
            train_count=len(train),
            test_count=len(test),
            val_count=len(val),
            train_sample=train[:5],
            test_sample=test[:5],
            pipeline_metadata=metadata,
        )
