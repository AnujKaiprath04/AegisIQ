import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_explain_prediction_shap_lime(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/xai/explain",
        json={
            "model_id": "customer_churn_xgboost",
            "input_features": {
                "monthly_support_tickets": 8,
                "csm_nps_score": 32,
                "monthly_active_users": 45,
                "contract_tenure_months": 14,
            },
            "prediction_probability": 0.74,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    expl = data["explanation"]
    assert expl["model_id"] == "customer_churn_xgboost"
    assert expl["prediction_label"] == "HIGH_CHURN_RISK"
    assert len(expl["shap_values"]) >= 4
    assert len(expl["lime_values"]) >= 3
    assert "support_tickets" in expl["natural_language_explanation"]


def test_counterfactual_simulation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/xai/counterfactual",
        json={
            "model_id": "customer_churn_xgboost",
            "input_features": {
                "monthly_support_tickets": 8,
                "csm_nps_score": 32,
                "monthly_active_users": 45,
            },
            "current_probability": 0.74,
            "target_probability": 0.18,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    sc = data["scenario"]
    assert sc["original_probability"] == 0.74
    assert sc["target_probability"] == 0.18
    assert "monthly_support_tickets" in sc["feature_interventions"]
    assert sc["feasibility_score"] > 0.80


def test_get_global_feature_importance(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/xai/feature-importance/customer_churn_xgboost",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["model_id"] == "customer_churn_xgboost"
    assert data["total_features"] >= 5
    top_feature = data["rankings"][0]
    assert top_feature["rank"] == 1
    assert top_feature["importance_score"] > 0.30


def test_get_model_transparency_card(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/xai/model-transparency/customer_churn_xgboost",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    card = data["card"]
    assert card["model_id"] == "customer_churn_xgboost"
    assert card["disparate_impact_ratio"] == 1.04
    assert "COMPLIANT" in card["compliance_status"]
    assert card["training_records_count"] > 10000
