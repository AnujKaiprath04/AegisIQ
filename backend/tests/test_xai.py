import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_global_feature_importance(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/xai/global-importance",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "features" in data
    assert len(data["features"]) >= 4
    assert any("Seats" in f["feature_name"] for f in data["features"])
    assert data["base_value"] > 0.0


def test_local_waterfall_explanation(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/xai/explain",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["base_value"] > 0
    assert data["predicted_value"] > 0
    assert len(data["contributions"]) >= 3
    assert data["explanation_method"] is not None


def test_what_if_counterfactual_simulation(client: TestClient):
    token = get_auth_token(client)
    
    sim_payload = {
        "weekly_active_seats_pct": 85.0,  # High usage
        "invoice_overdue_days": 0,        # Zero overdue
        "support_ticket_count": 0,        # Zero open tickets
        "contract_length_months": 36,     # 3-year commitment
    }
    res = client.post(
        "/api/v1/xai/what-if",
        json=sim_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["simulated_churn_probability_pct"] < data["original_churn_probability_pct"]
    assert data["delta_pct"] < 0  # Churn risk reduced
    assert "LOW_RISK" in data["risk_tier_change"] or "MEDIUM_RISK" in data["risk_tier_change"]


def test_model_fairness_audit(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/xai/fairness",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["disparate_impact_ratio"] >= 0.80
    assert data["fairness_verdict"] == "CERTIFIED_FAIR"
    assert data["demographic_parity_score"] > 90.0
