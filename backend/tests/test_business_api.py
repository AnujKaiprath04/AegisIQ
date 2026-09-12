import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_registered_tools(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/tools",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    tools = res.json()
    assert len(tools) >= 5
    names = [t["name"] for t in tools]
    assert "query_financial_kpis" in names
    assert "synthesize_sql_query" in names
    assert "trigger_quarantine_action" in names
    assert "export_executive_report" in names
    assert "fetch_dataset_quality_score" in names


def test_execute_financial_kpis_tool(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/tools/execute",
        json={"tool_name": "query_financial_kpis", "arguments": {"period": "Q1 2026"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "$24,800,000" in data["result"]["metrics"]["annual_recurring_revenue"]


def test_execute_sql_synthesis_tool(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/tools/execute",
        json={"tool_name": "synthesize_sql_query", "arguments": {"natural_language_question": "Show churn risk accounts"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "SELECT" in data["result"]["synthesized_sql"]
    assert data["result"]["is_read_only"] is True


def test_execute_siem_quarantine_tool(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/tools/execute",
        json={"tool_name": "trigger_quarantine_action", "arguments": {"target_ip": "198.51.100.99", "reason": "Brute-force attack"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["result"]["isolation_status"] == "ENFORCED"


def test_unified_decision_bridge_query(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/decision-bridge/query",
        json={
            "query": "What is our Q1 ARR and what security protocols protect access?",
            "persona": "CEO",
            "enable_tools": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["response"]) > 50
    assert data["confidence_score"] > 0.60
    assert len(data["citations"]) > 0
    assert len(data["recommendations"]) > 0
    assert data["latency_ms"] > 0


def test_decision_platform_manifest(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/decision-bridge/manifest",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_part2_modules"] == 12
    assert data["completion_percentage"] == 100.0
    assert len(data["modules_completed"]) == 12
    for mod in data["modules_completed"]:
        assert mod["status"] == "VERIFIED_ACTIVE"
