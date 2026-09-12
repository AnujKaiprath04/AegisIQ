import pytest
from fastapi.testclient import TestClient

from app.data_prep_pipeline.imputer import MissingValueImputer
from app.data_prep_pipeline.scaler import FeatureScaler
from app.data_prep_pipeline.encoder import CategoricalEncoder
from app.data_prep_pipeline.engineer import FeatureEngineer
from app.data_prep_pipeline.splitter import DatasetSplitter
from app.data_prep_pipeline.types import (
    EncodingMethod,
    ImputationStrategy,
    ScalingMethod,
    SplitMethod,
)


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_missing_value_imputation():
    records = [
        {"age": 30, "salary": 100000, "dept": "Sales"},
        {"age": None, "salary": 120000, "dept": "Engineering"},
        {"age": 40, "salary": None, "dept": None},
    ]
    imputed, stats = MissingValueImputer.impute(records, num_strategy=ImputationStrategy.MEAN, cat_strategy=ImputationStrategy.MODE)
    assert len(imputed) == 3
    assert imputed[1]["age"] == 35.0  # (30+40)/2
    assert imputed[2]["salary"] == 110000.0  # (100k+120k)/2
    assert imputed[2]["dept"] in ["Sales", "Engineering"]


def test_feature_scaling():
    records = [
        {"val": 10.0},
        {"val": 20.0},
        {"val": 30.0},
    ]
    scaled_std, params_std = FeatureScaler.fit_transform(records, method=ScalingMethod.STANDARD)
    assert scaled_std[1]["val"] == 0.0  # Mean is 20, z-score is 0.0

    scaled_mm, params_mm = FeatureScaler.fit_transform(records, method=ScalingMethod.MINMAX)
    assert scaled_mm[0]["val"] == 0.0
    assert scaled_mm[2]["val"] == 1.0


def test_categorical_encoding():
    records = [
        {"region": "North", "score": 10},
        {"region": "South", "score": 20},
        {"region": "North", "score": 30},
    ]
    encoded_ohe, meta_ohe = CategoricalEncoder.fit_transform(records, method=EncodingMethod.ONE_HOT)
    assert "region_north" in encoded_ohe[0]
    assert encoded_ohe[0]["region_north"] == 1.0
    assert encoded_ohe[1]["region_south"] == 1.0

    encoded_ord, meta_ord = CategoricalEncoder.fit_transform(records, method=EncodingMethod.ORDINAL)
    assert isinstance(encoded_ord[0]["region"], int)


def test_feature_engineering_datetimes():
    records = [
        {"timestamp": "2026-08-31T10:00:00Z", "amount": 500},
        {"timestamp": "2026-09-01T15:30:00Z", "amount": 800},
    ]
    engineered, meta = FeatureEngineer.engineer_features(records, extract_datetimes=True)
    assert len(engineered) == 2
    assert engineered[0]["timestamp_year"] == 2026
    assert engineered[0]["timestamp_month"] == 8
    assert "timestamp_day_of_week" in engineered[0]


def test_dataset_splitting():
    records = [{"id": i, "label": i % 2} for i in range(20)]
    train, test, val = DatasetSplitter.split(records, train_ratio=0.70, test_ratio=0.15, val_ratio=0.15, method=SplitMethod.RANDOM)
    assert len(train) == 14
    assert len(test) == 3
    assert len(val) == 3


def test_end_to_end_data_prep_api(client: TestClient):
    token = get_auth_token(client)
    payload = {
        "records": [
            {"account_id": "ACC-1", "mrr": 5000, "region": "US", "created_at": "2026-01-15T00:00:00Z", "churn": 0},
            {"account_id": "ACC-2", "mrr": None, "region": "EU", "created_at": "2026-02-10T00:00:00Z", "churn": 1},
            {"account_id": "ACC-3", "mrr": 8000, "region": "US", "created_at": "2026-03-05T00:00:00Z", "churn": 0},
            {"account_id": "ACC-4", "mrr": 12000, "region": None, "created_at": "2026-04-20T00:00:00Z", "churn": 0},
            {"account_id": "ACC-5", "mrr": 3000, "region": "APAC", "created_at": "2026-05-12T00:00:00Z", "churn": 1},
        ],
        "config": {
            "target_column": "churn",
            "numerical_imputation": "MEAN",
            "categorical_imputation": "MODE",
            "scaling": "STANDARD",
            "encoding": "ONE_HOT",
            "engineer_datetimes": True,
            "train_ratio": 0.60,
            "test_ratio": 0.20,
            "val_ratio": 0.20,
        },
    }
    res = client.post(
        "/api/v1/ml/data-prep/process",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 5
    assert data["target_column"] == "churn"
    assert data["train_count"] > 0
    assert len(data["feature_names"]) > 0


def test_list_data_prep_presets_api(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/data-prep/presets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["presets"]) >= 3
    preset_names = [p["preset"] for p in data["presets"]]
    assert "CHURN_PREDICTION" in preset_names
    assert "REVENUE_FORECAST" in preset_names
    assert "SIEM_ANOMALY" in preset_names
