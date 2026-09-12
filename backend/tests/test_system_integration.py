import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_system_integration_health_check(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/integration/system/health",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    health = data["health"]
    assert "FULLY_INTEGRATED_AND_OPERATIONAL" in health["overall_status"]
    assert health["total_subsystems"] >= 18
    assert health["operational_count"] == health["total_subsystems"]

    # Verify representation of all 3 parts
    parts_represented = {s["part"] for s in health["subsystems"]}
    assert "Part 1" in parts_represented
    assert "Part 2" in parts_represented
    assert "Part 3" in parts_represented


def test_master_cross_part_pipeline_execution(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/integration/system/master-pipeline",
        json={
            "account_id": "ACC-APEX-001",
            "company_name": "Apex Global Logistics",
            "support_tickets_30d": 12,
            "nps_score": 4,
            "license_utilization_pct": 34.0,
            "arr_usd": 480000.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    pipe = data["pipeline"]
    assert pipe["status"] == "SUCCESS_ALL_3_PARTS_COORDINATED"
    assert pipe["execution_time_ms"] > 0.0

    # Part 1 check
    assert pipe["part1_account_data"]["account_id"] == "ACC-APEX-001"
    assert pipe["part1_audit_logged"] is True

    # Part 3 Predictive check
    assert pipe["part3_prediction"]["churn_probability"] >= 0.60

    # Part 3 XAI check
    assert "monthly_support_tickets" in pipe["part3_xai_attribution"]["top_shap_driver"]

    # Part 2 RAG check
    assert "Tier-1" in pipe["part2_rag_playbook"]["title"]

    # Part 2 AI Synthesis check
    assert "AI Copilot Analysis" in pipe["part2_ai_synthesis"]

    # Part 3 Alert Dispatch check
    assert pipe["part3_alert_dispatched"]["severity"] in ["CRITICAL", "HIGH"]



def test_service_topology_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/integration/system/topology",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] >= 8
    node_ids = [n["id"] for n in data["nodes"]]
    assert "layer-frontend" in node_ids
    assert "layer-gateway" in node_ids
    assert "layer-part1" in node_ids
    assert "layer-part2" in node_ids
    assert "layer-part3" in node_ids
