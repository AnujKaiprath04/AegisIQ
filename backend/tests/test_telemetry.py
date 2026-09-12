import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_root_health_and_metrics_endpoints(client: TestClient):
    # 1. Test /health
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # 2. Test /metrics
    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "# HELP" in metrics_res.text
    assert "# TYPE" in metrics_res.text
    assert "aegisiq_uptime_seconds" in metrics_res.text


def test_telemetry_dashboard_snapshot(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/telemetry/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["platform_status"] == "OPERATIONAL"
    assert len(data["subsystems"]) == 6
    assert data["resources"]["cpu_usage_pct"] > 0
    assert data["db_pool"]["pool_size"] == 20
    assert data["apm"]["requests_per_second"] > 0
    assert data["apm"]["p50_latency_ms"] > 0


def test_subsystem_health_probing(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/telemetry/subsystems",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    subsystems = res.json()
    assert len(subsystems) == 6
    assert all(s["status"] == "HEALTHY" for s in subsystems)
    names = [s["name"] for s in subsystems]
    assert "FastAPI Gateway Core" in names
    assert "PostgreSQL 16 HA Cluster" in names
    assert "Redis 7 In-Memory Broker" in names


def test_database_pool_telemetry(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/telemetry/db-pool",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pool_size"] == 20
    assert data["checked_in_connections"] >= 0
    assert data["pool_utilization_pct"] >= 0.0
