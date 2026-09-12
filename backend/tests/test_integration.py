import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_data_connections(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/integration/connections",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    conns = res.json()
    assert isinstance(conns, list)
    assert len(conns) >= 4
    assert any(c["connection_type"] == "POSTGRESQL" for c in conns)


def test_create_and_test_connection_diagnostics(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Register a new connection
    conn_payload = {
        "name": "APAC Regional SQLite Replica",
        "description": "Replica data node for Tokyo and Singapore operations",
        "connection_type": "SQLITE",
        "connection_string": "sqlite:///./test_aegisiq.db",
        "database_name": "apac_ops",
        "ssl_enabled": True,
    }
    create_res = client.post(
        "/api/v1/integration/connections",
        json=conn_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    conn_id = created["id"]
    assert created["name"] == "APAC Regional SQLite Replica"

    # 2. Run diagnostic health test
    test_res = client.post(
        f"/api/v1/integration/connections/{conn_id}/test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert test_res.status_code == 200
    diag = test_res.json()
    assert diag["success"] is True
    assert diag["status"] == "ACTIVE"
    assert diag["latency_ms"] >= 0.0

    # 3. Retrieve schema tree
    schema_res = client.get(
        f"/api/v1/integration/connections/{conn_id}/schema",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert schema_res.status_code == 200
    schema_data = schema_res.json()
    assert schema_data["connection_id"] == conn_id
    assert "tables" in schema_data


def test_ingestion_job_lifecycle(client: TestClient):
    token = get_auth_token(client)
    
    # Get connections
    conns_res = client.get("/api/v1/integration/connections", headers={"Authorization": f"Bearer {token}"})
    assert conns_res.status_code == 200
    conn_id = conns_res.json()[0]["id"]

    # 1. Create Ingestion Job
    job_payload = {
        "connection_id": conn_id,
        "job_name": "Daily Enterprise Ledger Sync",
        "sync_mode": "FULL_SYNC",
        "sync_schedule": "DAILY",
    }
    job_res = client.post(
        "/api/v1/integration/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert job_res.status_code == 201
    job = job_res.json()
    job_id = job["id"]
    assert job["status"] == "PENDING"

    # 2. Execute Ingestion Job
    run_res = client.post(
        f"/api/v1/integration/jobs/{job_id}/run",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "SUCCESS"
    assert run_data["rows_ingested"] > 0
