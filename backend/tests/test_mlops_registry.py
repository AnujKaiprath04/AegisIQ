import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_registered_models(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_models"] >= 6
    ids = [m["model_id"] for m in data["models"]]
    assert "customer_churn_xgboost" in ids
    assert "revenue_forecast_arima" in ids
    assert "isolation_forest_anomalies" in ids


def test_trigger_model_retraining(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/models/customer_churn_xgboost/retrain",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["model_id"] == "customer_churn_xgboost"
    assert data["status"] == "COMPLETED_SUCCESS"
    assert data["improvement_pct"] > 0.0


def test_get_model_drift_metrics(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/models/customer_churn_xgboost/drift",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["model_id"] == "customer_churn_xgboost"
    assert data["total_features"] >= 3
    for m in data["metrics"]:
        assert m["psi_score"] < 0.10  # No drift
        assert m["drift_status"] == "NO_DRIFT"


def test_canary_deployment_and_promotion(client: TestClient):
    token = get_auth_token(client)
    # 1. Deploy canary 15%
    res1 = client.post(
        "/api/v1/ml/models/customer_churn_xgboost/deploy-canary",
        json={"canary_split_pct": 15.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200
    assert res1.json()["canary_traffic_split_pct"] == 15.0

    # 2. Promote canary to active production
    res2 = client.post(
        "/api/v1/ml/models/customer_churn_xgboost/promote",
        json={"version_str": "v2.5.0-rc1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["active_version"] == "v2.5.0-rc1"
    assert data2["canary_traffic_split_pct"] == 0.0


def test_master_intelligence_bridge_status(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/master-bridge/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_modules_active"] == 10
    assert "HEALTHY" in data["system_health"]
    assert data["active_models_count"] >= 7
    assert data["active_recommendations_count"] >= 7
    assert data["composite_risk_score"] < 30.0


def test_master_intelligence_bridge_full_sweep(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/master-bridge/full-sweep",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["execution_status"] == "SUCCESSFUL_10_MODULE_SWEEP"
    assert len(data["modules_evaluated"]) == 10
    assert "projected_arr_next_quarter_m" in data["predictive_signals"]
    assert data["prescriptive_recommendations_count"] >= 7
    assert data["composite_business_risk_score"] > 0
    assert data["zero_trust_security_score"] <= 25.0
