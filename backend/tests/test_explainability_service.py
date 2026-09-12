import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_inspect_decision_trajectory(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/explainability/inspect",
        json={"query": "What are our mandatory ISO 27001 access control protocols?", "persona": "CISO"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["grounding_status"] == "VERIFIED_GROUNDED"
    assert len(data["reasoning_steps"]) >= 4
    assert data["average_similarity_score"] > 0.50
    assert "cosine_similarity_mean" in data["confidence_calibration"]


def test_citation_graph_dag_generation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/explainability/citation-graph",
        json={"query": "What is our Q1 2026 ARR and gross profit margin?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    graph = data["graph"]
    assert graph["total_nodes"] >= 3
    assert graph["total_edges"] >= 2
    
    node_types = [n["node_type"] for n in graph["nodes"]]
    assert "QUERY" in node_types
    assert "CLAIM" in node_types
    assert "PASSAGE" in node_types or "DOCUMENT" in node_types


def test_ai_audit_logging(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/explainability/audit-logs?limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 2
    record = logs[0]
    assert "audit_id" in record
    assert record["confidence_score"] > 0.0
    assert record["compliance_status"] in ["VERIFIED_GROUNDED", "LOW_CONFIDENCE_REVIEW"]


def test_explainability_telemetry_stats(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/explainability/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["grounding_pass_rate_percentage"] > 90.0
    assert data["average_decision_confidence"] > 0.80
    assert len(data["compliance_standards"]) >= 2
