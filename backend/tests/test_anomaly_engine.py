import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_detect_stream_anomaly_normal_value(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/anomalies/detect-stream",
        json={
            "domain": "FINANCIAL",
            "value": 2450.0,
            "method": "Z_SCORE",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["point"]["is_anomaly"] is False
    assert data["point"]["severity"] == "NORMAL"
    assert data["point"]["anomaly_score"] == 0.0


def test_detect_stream_anomaly_extreme_outlier(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/anomalies/detect-stream",
        json={
            "domain": "FINANCIAL",
            "value": 18500.0,
            "method": "Z_SCORE",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["point"]["is_anomaly"] is True
    assert data["point"]["severity"] == "CRITICAL"
    assert data["point"]["anomaly_score"] > 0.90


def test_detect_batch_anomalies(client: TestClient):
    token = get_auth_token(client)
    # 20 normal numbers around 100, plus two extreme outliers (2500.0, -1500.0)
    values = [100.0 + (i % 5) for i in range(20)] + [2500.0, -1500.0]
    res = client.post(
        "/api/v1/ml/anomalies/detect-batch",
        json={
            "values": values,
            "method": "Z_SCORE",
            "threshold": 2.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["result"]["total_records"] == 22
    assert data["result"]["anomaly_count"] >= 2
    assert len(data["result"]["anomalies"]) >= 2



def test_get_anomaly_profiles(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/anomalies/profiles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_profiles"] == 4
    domains = [p["domain"] for p in data["profiles"]]
    assert "FINANCIAL" in domains
    assert "SYSTEM_TELEMETRY" in domains
    assert "USER_BEHAVIOR" in domains
    assert "REVENUE" in domains


def test_get_recent_anomalies(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/anomalies/recent",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_recent_anomalies"] >= 3
    for a in data["anomalies"]:
        assert a["is_anomaly"] is True
