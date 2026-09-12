from pathlib import Path
import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_qa_summary_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/qa/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    rep = data["report"]
    assert rep["total_test_cases"] >= 180
    assert rep["total_failed"] == 0
    assert rep["overall_pass_rate_pct"] == 100.0
    assert rep["code_coverage_pct"] >= 90.0
    assert len(rep["suites"]) >= 4


def test_qa_load_profiles_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/qa/load-profiles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_profiles"] >= 2
    tools = [p["tool"] for p in data["profiles"]]
    assert any("Locust" in t for t in tools)
    assert any("K6" in t for t in tools)


def test_qa_e2e_specs_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/qa/e2e-specs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_specs"] >= 4
    workflow_names = [s["workflow_name"] for s in data["specs"]]
    assert any("Authentication" in name for name in workflow_names)
    assert any("Dashboard" in name for name in workflow_names)
    assert any("Copilot" in name for name in workflow_names)


def test_qa_test_automation_files_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    locust_file = repo_root / "tests" / "load" / "locustfile.py"
    k6_file = repo_root / "tests" / "load" / "k6_load_test.js"
    playwright_file = repo_root / "tests" / "e2e" / "playwright.spec.ts"
    postman_file = repo_root / "tests" / "postman" / "AegisIQ_API_Collection.json"

    assert locust_file.exists()
    assert k6_file.exists()
    assert playwright_file.exists()
    assert postman_file.exists()

    # Content assertions
    locust_content = locust_file.read_text(encoding="utf-8")
    assert "HttpUser" in locust_content
    assert "/api/v1/ml/predictions/churn" in locust_content

    k6_content = k6_file.read_text(encoding="utf-8")
    assert "p(99)<500" in k6_content
    assert "target: 500" in k6_content

    pw_content = playwright_file.read_text(encoding="utf-8")
    assert "test.describe" in pw_content
    assert "admin@aegisiq.com" in pw_content

    postman_content = postman_file.read_text(encoding="utf-8")
    assert "AegisIQ Enterprise Platform REST API Collection" in postman_content
