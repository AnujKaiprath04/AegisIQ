import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]



def test_revenue_forecast_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/revenue-forecast",
        json={"historical_baseline_arr": 24800000.0, "horizon_quarters": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["historical_baseline_arr"] == 24800000.0
    assert len(data["forecast_points"]) == 4
    assert data["forecast_points"][-1]["predicted_value"] > 24800000.0
    assert data["metrics"]["r_squared"] > 0.95


def test_customer_churn_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/customer-churn",
        json={
            "account_id": "ACC-APEX-001",
            "company_name": "Apex Global Logistics",
            "license_utilization_pct": 34.0,
            "support_tickets_last_30d": 12,
            "nps_score": 4,
            "days_to_renewal": 45,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["churn_probability"] > 0.60
    assert data["risk_tier"] == "CRITICAL_RISK"
    assert len(data["top_drivers"]) >= 2
    assert "Solutions Architect" in data["recommended_action"]


def test_demand_forecast_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/demand-forecast",
        json={"sku_id": "SKU-ENT-SERVER-01", "product_name": "Enterprise Cloud Blade 128G", "horizon_months": 6},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == "SKU-ENT-SERVER-01"
    assert len(data["forecast_units"]) == 6
    assert "Peak" in data["peak_demand_period"] or "Units" in data["peak_demand_period"]


def test_employee_attrition_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/employee-attrition",
        json={
            "employee_id": "EMP-ENG-442",
            "role": "Senior Distributed Systems Engineer",
            "department": "Engineering",
            "comp_ratio": 0.82,
            "tenure_years": 3.2,
            "promotions_last_3yr": 0,
            "engagement_score": 6.2,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["attrition_probability"] > 0.40
    assert len(data["primary_drivers"]) >= 2


def test_inventory_optimization_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/inventory-optimization",
        json={
            "sku_id": "SKU-OPT-100",
            "product_name": "Enterprise Fiber Switch 48-Port",
            "annual_demand_units": 12000,
            "order_cost_usd": 250.0,
            "unit_holding_cost_usd": 45.0,
            "lead_time_days": 14,
            "daily_demand_std_dev": 8.5,
            "service_level": 0.95,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["economic_order_quantity_units"] > 0
    assert data["safety_stock_units"] > 0
    assert data["reorder_point_units"] > 0
    assert data["estimated_annual_holding_cost_usd"] > 0


def test_customer_ltv_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/predictions/customer-ltv",
        json={
            "account_id": "ACC-NEXUS-002",
            "company_name": "Nexus FinTech Labs",
            "monthly_revenue_usd": 25000.0,
            "gross_margin_pct": 0.684,
            "monthly_churn_rate": 0.015,
            "annual_discount_rate": 0.08,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_lifetime_months"] > 50
    assert data["net_present_clv_usd"] > 500000.0
    assert "TIER_1" in data["customer_tier"]


def test_list_predictive_models_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/predictions/models",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_models"] == 7
    model_types = [m["type"] for m in data["models"]]
    assert "REVENUE_FORECAST" in model_types
    assert "CUSTOMER_CHURN" in model_types
    assert "INVENTORY_OPTIMIZATION" in model_types
    assert "CUSTOMER_LTV" in model_types
