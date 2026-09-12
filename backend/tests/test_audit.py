import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_admin_audit_logs_and_stats(client: TestClient):
    token = get_auth_token(client)

    # Query Logs
    logs_res = client.get("/api/v1/audit", headers={"Authorization": f"Bearer {token}"})
    assert logs_res.status_code == 200
    data = logs_res.json()
    assert "logs" in data
    assert data["total_count"] >= 1

    # Query Stats
    stats_res = client.get("/api/v1/audit/stats", headers={"Authorization": f"Bearer {token}"})
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_events" in stats
    assert "success_count" in stats
