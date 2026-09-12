import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_ai_query_executive_persona(client: TestClient):
    token = get_auth_token(client)
    
    query_payload = {
        "query": "Synthesize our quarterly ARR expansion rate and regional revenue trends.",
        "persona": "CEO_STRATEGIST",
        "include_sql_synthesis": True,
    }
    res = client.post(
        "/api/v1/assistant/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert "message" in data
    msg = data["message"]
    assert msg["role"] == "assistant"
    assert "24.8M" in msg["content"]
    assert len(msg["citations"]) > 0
    assert len(msg["recommendations"]) > 0
    assert msg["generated_sql"] is not None
    assert msg["latency_ms"] >= 0.0


def test_ai_query_financial_persona(client: TestClient):
    token = get_auth_token(client)
    
    query_payload = {
        "query": "Evaluate our monthly net burn rate and liquidity ratio.",
        "persona": "CFO_FINANCIAL",
        "include_sql_synthesis": True,
    }
    res = client.post(
        "/api/v1/assistant/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    msg = data["message"]
    assert "Quick Ratio" in msg["content"]
    assert "LTV:CAC" in msg["content"] or "CAC" in msg["content"]


def test_ai_prompt_templates_catalog(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/assistant/prompts?persona=CEO_STRATEGIST",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    prompts = res.json()
    assert len(prompts) >= 2
    assert all(p["persona"] == "CEO_STRATEGIST" for p in prompts)


def test_conversation_history_and_deletion(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Ask question to create a thread
    query_payload = {
        "query": "Perform a security audit scan for authentication anomalies.",
        "persona": "SECURITY_OFFICER",
    }
    res = client.post(
        "/api/v1/assistant/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    conv_id = res.json()["conversation_id"]

    # 2. List conversations
    convs_res = client.get(
        "/api/v1/assistant/conversations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert convs_res.status_code == 200
    convs = convs_res.json()
    assert any(c["id"] == conv_id for c in convs)

    # 3. Retrieve conversation detail
    detail_res = client.get(
        f"/api/v1/assistant/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["messages"]) >= 2  # user + assistant

    # 4. Delete conversation
    del_res = client.delete(
        f"/api/v1/assistant/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
