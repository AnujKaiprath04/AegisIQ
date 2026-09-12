import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_get_security_posture(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/security/posture",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["zero_trust_score"] <= 25.0  # Hardened zero-trust posture
    assert "HARDENED" in data["posture_status"]
    assert data["quarantined_ips_count"] >= 1
    assert len(data["vector_distribution"]) >= 6


def test_list_security_incidents(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/security/incidents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_incidents"] >= 6
    vectors = [i["vector_type"] for i in data["incidents"]]
    assert "BRUTE_FORCE" in vectors
    assert "LOGIN_ANOMALY" in vectors
    assert "API_MISUSE" in vectors
    assert "DATA_ACCESS_ANOMALY" in vectors


def test_filter_security_incidents_by_severity(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/security/incidents?severity=CRITICAL",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["incidents"]) >= 1
    for i in data["incidents"]:
        assert i["severity"] == "CRITICAL"


def test_analyze_brute_force_event(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/security/analyze-event",
        json={
            "event_type": "BRUTE_FORCE",
            "payload": {
                "source_ip": "198.51.100.99",
                "target_user": "security.admin@aegisiq.com",
                "failed_attempts_count": 64,
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["vector_type"] == "BRUTE_FORCE"
    assert data["severity"] == "CRITICAL"
    assert data["mitre_technique_id"] == "T1110.001"
    assert data["recommended_playbook"] == "EDGE_IP_QUARANTINE"


def test_execute_incident_mitigation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/security/incidents/inc-sec-003/mitigate",
        json={"action_type": "EDGE_IP_QUARANTINE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["incident"]["status"] == "QUARANTINED"
    assert data["incident"]["mitigated_at"] is not None


def test_get_mitre_attack_matrix(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/security/mitre-matrix",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_tactics_mapped"] == 6
    tech_ids = [m["technique_id"] for m in data["mappings"]]
    assert "T1078.004" in tech_ids
    assert "T1110.001" in tech_ids
    assert "T1020" in tech_ids
