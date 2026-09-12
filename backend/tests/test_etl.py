import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "data.analyst@aegisiq.com", password: str = "Data@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_etl_execution_and_quality_scorecard(client: TestClient):
    token = get_auth_token(client)
    
    # Get available datasets
    ds_res = client.get("/api/v1/datasets", headers={"Authorization": f"Bearer {token}"})
    assert ds_res.status_code == 200
    datasets = ds_res.json()
    assert len(datasets) > 0
    target_ds_id = datasets[0]["id"]

    # Execute cleaning pipeline
    etl_payload = {
        "dataset_id": target_ds_id,
        "pipeline_name": "Automated Quality & Deduplication Run",
        "remove_duplicates": True,
        "handle_missing": True,
        "missing_strategy": "auto",
        "handle_outliers": True,
        "outlier_method": "iqr",
        "outlier_action": "clip",
        "standardize_headers": True,
    }
    run_res = client.post(
        "/api/v1/etl/clean",
        json=etl_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "SUCCESS"
    assert run_data["rows_after"] > 0

    # Get Quality Scorecard
    qr_res = client.get(
        f"/api/v1/etl/quality-report/{target_ds_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert qr_res.status_code == 200
    qr_data = qr_res.json()
    assert "completeness" in qr_data
    assert "uniqueness" in qr_data
    assert qr_data["overall_score"] >= 90.0
