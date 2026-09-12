import io
import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "data.analyst@aegisiq.com", password: str = "Data@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_seeded_datasets(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/datasets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_upload_csv_dataset(client: TestClient):
    token = get_auth_token(client)
    csv_content = b"client_id,industry,revenue,churn_risk\nCUST-01,FinTech,120000,0.02\nCUST-02,HealthTech,95000,0.05\nCUST-03,Retail,60000,0.12\n"
    
    files = {
        "file": ("client_metrics.csv", io.BytesIO(csv_content), "text/csv"),
    }
    data = {
        "name": "Client Industry Metrics",
        "description": "Test upload of client metrics",
    }
    res = client.post(
        "/api/v1/datasets/upload",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    dataset = res.json()["dataset"]
    assert dataset["name"] == "Client Industry Metrics"
    assert dataset["row_count"] == 3
    dataset_id = dataset["id"]

    # Test Preview
    preview_res = client.get(
        f"/api/v1/datasets/{dataset_id}/preview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert preview_res.status_code == 200
    preview = preview_res.json()
    assert len(preview["columns"]) == 4
    assert len(preview["rows"]) == 3
