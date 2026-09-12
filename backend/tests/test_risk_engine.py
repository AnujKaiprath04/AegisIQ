import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_get_risk_scorecard(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/risks/scorecard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["composite_risk_score"] < 25.0  # Optimal low risk
    assert "OPTIMAL" in data["risk_status"]
    assert data["total_financial_exposure_usd"] > 800000.0
    assert len(data["pillar_breakdown"]) == 6
    assert data["active_risks_count"] >= 6


def test_list_risk_items(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/risks/items",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_risks"] >= 6
    assert data["total_financial_exposure_usd"] > 800000.0
    pillars = [r["pillar"] for r in data["risks"]]
    assert "CUSTOMER_LOSS" in pillars
    assert "REVENUE_DECLINE" in pillars
    assert "SUPPLY_CHAIN_DISRUPTION" in pillars
    assert "LOW_PERFORMING_PRODUCT" in pillars


def test_filter_risk_items_by_pillar(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/risks/items?pillar=CUSTOMER_LOSS",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["risks"]) >= 1
    for r in data["risks"]:
        assert r["pillar"] == "CUSTOMER_LOSS"


def test_evaluate_risk_domain(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/risks/evaluate",
        json={
            "pillar": "CUSTOMER_LOSS",
            "parameters": {
                "accounts_at_risk_arr": 550000.0,
                "top_5_concentration_pct": 32.0,
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["pillar"] == "CUSTOMER_LOSS"
    assert data["financial_exposure_usd"] == 550000.0
    assert len(data["mitigation_actions"]) >= 2


def test_risk_heatmap_data(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/risks/heatmap",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_points"] >= 6
    assert "5x5" in data["matrix_dimension"]
    for pt in data["points"]:
        assert 1 <= pt["likelihood"] <= 5
        assert 1 <= pt["impact"] <= 5
        assert pt["risk_score"] > 0
