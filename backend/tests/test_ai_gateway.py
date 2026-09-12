import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_ai_gateway_providers_list(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/gateway/providers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "providers" in data
    assert len(data["providers"]) >= 4
    names = [p["provider_type"] for p in data["providers"]]
    assert "LOCAL_ENTERPRISE" in names
    assert "GEMINI" in names
    assert "OPENAI" in names


def test_intent_classifier(client: TestClient):
    token = get_auth_token(client)
    
    # 1. RAG prompt
    rag_res = client.post(
        "/api/v1/ai/gateway/classify",
        json={"prompt": "What does Section 9.2 of the ISO 27001 security policy say about access control?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rag_res.status_code == 200
    assert rag_res.json()["intent"] == "ENTERPRISE_RAG"

    # 2. Business KPI prompt
    kpi_res = client.post(
        "/api/v1/ai/gateway/classify",
        json={"prompt": "Why is our gross profit margin and revenue increasing this quarter?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert kpi_res.status_code == 200
    assert kpi_res.json()["intent"] == "BUSINESS_ANALYTICS"

    # 3. Report prompt
    rep_res = client.post(
        "/api/v1/ai/gateway/classify",
        json={"prompt": "Generate an executive report and quarterly brief for the board"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rep_res.status_code == 200
    assert rep_res.json()["intent"] == "EXECUTIVE_REPORT"


def test_gateway_chat_dispatch(client: TestClient):
    token = get_auth_token(client)
    
    chat_payload = {
        "prompt": "Summarize our current ARR and customer churn risk trajectory",
        "provider_type": "LOCAL_ENTERPRISE",
        "system_persona": "CFO",
    }
    res = client.post(
        "/api/v1/ai/gateway/chat",
        json=chat_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert len(data["response"]) > 50
    assert data["latency_ms"] > 0
    assert data["tokens_estimated"] > 0
    assert data["intent"] in ["BUSINESS_ANALYTICS", "EXECUTIVE_REPORT", "CONVERSATIONAL_QA"]


def test_gateway_telemetry(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/gateway/telemetry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["gateway_status"] == "HEALTHY"
    assert data["total_requests_processed"] > 0
