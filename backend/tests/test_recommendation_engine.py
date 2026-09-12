import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_recommendations(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/recommendations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_recommendations"] >= 7
    assert data["total_potential_roi_usd"] > 500000.0
    assert len(data["recommendations"]) >= 7
    # Verify sorting by expected ROI descending
    rois = [r["expected_roi_usd"] for r in data["recommendations"]]
    assert rois == sorted(rois, reverse=True)


def test_filter_recommendations_by_category(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/recommendations?category=COST_OPTIMIZATION",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommendations"]) >= 1
    for r in data["recommendations"]:
        assert r["category"] == "COST_OPTIMIZATION"


def test_generate_account_retention_recommendation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/recommendations/generate",
        json={
            "target_type": "ACCOUNT",
            "target_id": "ACC-APEX-999",
            "parameters": {
                "company_name": "Apex Global Logistics",
                "churn_probability": 0.82,
                "arr_usd": 650000.0,
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["generated_count"] >= 1
    rec = data["recommendations"][0]
    assert rec["category"] == "CUSTOMER_RETENTION"
    assert rec["priority"] == "CRITICAL"
    assert rec["expected_roi_usd"] > 500000.0
    assert len(rec["action_steps"]) >= 3


def test_generate_inventory_restocking_recommendation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/recommendations/generate",
        json={
            "target_type": "INVENTORY",
            "target_id": "SKU-SWITCH-88",
            "parameters": {
                "product_name": "Enterprise Optical Switch",
                "current_stock": 20,
                "reorder_point": 120,
                "unit_price_usd": 350.0,
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["generated_count"] >= 1
    rec = data["recommendations"][0]
    assert rec["category"] == "INVENTORY_RESTOCKING"
    assert rec["priority"] == "HIGH"


def test_apply_recommendation(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/recommendations/rec-ret-001/apply",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["recommendation"]["status"] == "APPLIED"
    assert data["recommendation"]["applied_at"] is not None


def test_recommendation_categories_summary(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/recommendations/categories",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_categories"] == 7
    assert data["total_potential_roi_all_categories_usd"] > 800000.0
    cats = [c["category"] for c in data["categories"]]
    assert "CUSTOMER_RETENTION" in cats
    assert "PRODUCT_PROMOTION" in cats
    assert "INVENTORY_RESTOCKING" in cats
    assert "COST_OPTIMIZATION" in cats
