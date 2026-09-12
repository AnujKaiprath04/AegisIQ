import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_bi_executive_overview(client: TestClient):
    token = get_auth_token(client)
    res = client.get("/api/v1/bi/overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "summary_metrics" in data
    assert "revenue_trend" in data
    assert len(data["summary_metrics"]) >= 4


def test_kpi_engine_and_calculation(client: TestClient):
    token = get_auth_token(client)
    
    # List KPIs
    kpi_res = client.get("/api/v1/kpis", headers={"Authorization": f"Bearer {token}"})
    assert kpi_res.status_code == 200
    kpis = kpi_res.json()
    assert len(kpis) >= 7

    # Calculate custom KPI formula
    calc_payload = {
        "formula_type": "GROSS_MARGIN",
        "parameters": {
            "revenue": 5000000,
            "cogs": 1500000,
        },
    }
    calc_res = client.post(
        "/api/v1/kpis/calculate",
        json=calc_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["calculated_value"] == 70.0
    assert calc_data["unit"] == "%"
