import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_zero_trust_scorecard_retrieval(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/cybersecurity/scorecard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert 0.0 <= data["overall_risk_score"] <= 100.0
    assert data["auth_entropy_score"] >= 90.0
    assert data["rbac_enclosure_score"] == 100.0
    assert data["encryption_score"] == 100.0


def test_list_and_filter_siem_incidents(client: TestClient):
    token = get_auth_token(client)
    
    # 1. List all
    res = client.get(
        "/api/v1/cybersecurity/incidents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 3

    # 2. Filter by severity
    res_high = client.get(
        "/api/v1/cybersecurity/incidents?severity=HIGH",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_high.status_code == 200
    high_incs = res_high.json()
    assert all(i["severity"] == "HIGH" for i in high_incs)


def test_remediation_action_block_ip(client: TestClient):
    token = get_auth_token(client)
    
    # Get first open incident
    incs_res = client.get("/api/v1/cybersecurity/incidents", headers={"Authorization": f"Bearer {token}"})
    inc_id = incs_res.json()[0]["id"]

    # Trigger action
    action_res = client.post(
        f"/api/v1/cybersecurity/incidents/{inc_id}/action",
        json={"action": "BLOCK_IP"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert action_res.status_code == 200
    action_data = action_res.json()
    assert action_data["status"] == "MITIGATED"
    assert "quarantined" in action_data["message"] or "blocked" in action_data["message"]


def test_ip_blocklist_crud(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Add IP to blocklist
    add_res = client.post(
        "/api/v1/cybersecurity/blocklist",
        json={"ip_address": "198.51.100.77", "reason": "DDoS flood traffic pattern", "is_permanent": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_res.status_code == 201
    assert add_res.json()["ip_address"] == "198.51.100.77"

    # 2. List blocklist
    list_res = client.get(
        "/api/v1/cybersecurity/blocklist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_res.status_code == 200
    blocks = list_res.json()
    assert any(b["ip_address"] == "198.51.100.77" for b in blocks)
