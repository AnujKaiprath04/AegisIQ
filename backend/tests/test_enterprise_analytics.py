import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_get_analytics_overview(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "$24.8M" in data["financial_forecast"]["current_arr"]
    assert data["churn_risk_summary"]["accounts_at_risk"] > 0
    assert data["active_models_count"] >= 6
    assert data["average_model_confidence"] > 0.90


def test_dispatch_revenue_forecast_job(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/analytics/dispatch",
        json={"job_type": "REVENUE_FORECAST", "parameters": {"horizon_months": 12}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["job_type"] == "REVENUE_FORECAST"
    assert data["predictions"]["forecast_arr_next_period"] == 33200000.0
    assert data["metrics"]["r_squared"] > 0.95


def test_dispatch_churn_analysis_job(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/analytics/dispatch",
        json={"job_type": "CUSTOMER_CHURN_ANALYSIS", "parameters": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert len(data["predictions"]["high_risk_cohort"]) >= 3
    assert data["metrics"]["roc_auc"] > 0.90


def test_dispatch_anomaly_scan_job(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/analytics/dispatch",
        json={"job_type": "ANOMALY_DETECTION_SCAN", "parameters": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["predictions"]["anomalies_detected_count"] > 0


def test_dispatch_cross_domain_sweep(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/analytics/dispatch",
        json={"job_type": "CROSS_DOMAIN_SWEEP", "parameters": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["predictions"]["sweep_status"] == "FULL_CROSS_DOMAIN_SYNC_COMPLETE"


def test_analytics_telemetry(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/analytics/telemetry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["engine_status"] == "OPERATIONAL"
    assert len(data["active_ml_models"]) >= 6
    assert data["total_inferences_served"] > 0
    assert data["average_inference_latency_ms"] > 0
