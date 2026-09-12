import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_personas(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/assistant/personas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["personas"]) == 5
    types = [p["persona_type"] for p in data["personas"]]
    assert "CEO" in types
    assert "CFO" in types
    assert "CTO" in types
    assert "CISO" in types
    assert "BI_ANALYST" in types


def test_assistant_chat_across_personas(client: TestClient):
    token = get_auth_token(client)
    
    # 1. CEO chat
    ceo_res = client.post(
        "/api/v1/ai/assistant/chat",
        json={
            "query": "Summarize our quarterly strategic growth and market expansion trajectory",
            "persona": "CEO",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ceo_res.status_code == 200
    ceo_data = ceo_res.json()
    assert ceo_data["persona"] == "CEO"
    assert len(ceo_data["response"]) > 50
    assert len(ceo_data["recommendations"]) > 0

    # 2. CFO chat
    cfo_res = client.post(
        "/api/v1/ai/assistant/chat",
        json={
            "query": "Why are our gross profit margins expanding and what is the ARR projection?",
            "persona": "CFO",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cfo_res.status_code == 200
    assert cfo_res.json()["persona"] == "CFO"


def test_business_recommendations_generation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/assistant/recommendations",
        json={"topic": "Revenue expansion and customer retention", "persona": "CFO"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommendations"]) >= 2
    for card in data["recommendations"]:
        assert card["expected_impact_usd"] > 0
        assert card["effort_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert card["department"] is not None


def test_kpi_root_cause_explanation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/assistant/kpi-explain",
        json={"kpi_name": "Annual Recurring Revenue ARR", "persona": "CFO"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "$24.8M" in data["current_value"] or "ARR" in data["kpi_name"]
    assert len(data["primary_drivers"]) >= 2
    assert len(data["recommended_actions"]) >= 2
