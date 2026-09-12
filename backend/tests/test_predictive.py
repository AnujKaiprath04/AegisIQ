import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_time_series_revenue_forecast(client: TestClient):
    token = get_auth_token(client)
    
    # Test 12-month horizon
    res = client.get(
        "/api/v1/predictive/forecast/revenue?horizon_months=12",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["horizon_months"] == 12
    assert data["r2_score"] >= 0.90
    assert len(data["data_points"]) >= 8  # 5 historical + 4 forecast
    
    # Assert confidence bounds validity
    for dp in data["data_points"]:
        if dp["is_forecast"]:
            assert dp["lower_bound_95"] <= dp["predicted_value"] <= dp["upper_bound_95"]


def test_customer_churn_predictions(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/predictive/churn/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    churn_data = res.json()
    assert churn_data["total_accounts_evaluated"] >= 5
    assert churn_data["high_risk_count"] >= 1
    assert churn_data["arr_at_risk"] > 0
    assert len(churn_data["accounts"]) >= 5
    
    first_acc = churn_data["accounts"][0]
    assert 0.0 <= first_acc["churn_probability_pct"] <= 100.0
    assert len(first_acc["top_risk_factors"]) > 0


def test_ml_model_registry_and_retraining(client: TestClient):
    # Admin role for retrain
    admin_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
    )
    token = admin_res.json()["access_token"]

    # 1. List models
    models_res = client.get(
        "/api/v1/predictive/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert models_res.status_code == 200
    models = models_res.json()
    assert len(models) >= 3
    model_id = models[0]["id"]

    # 2. Retrain model
    retrain_res = client.post(
        f"/api/v1/predictive/models/{model_id}/retrain",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert retrain_res.status_code == 200
    retrain_data = retrain_res.json()
    assert retrain_data["status"] == "TRAINED"
    assert retrain_data["new_accuracy_score"] > 0.90
