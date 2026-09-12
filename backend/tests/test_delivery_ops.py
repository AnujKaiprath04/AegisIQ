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


def test_delivery_manifest_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/delivery/manifest",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    mf = data["manifest"]
    assert mf["version"] == "1.0.0"
    assert mf["release_tag"] == "v1.0.0-GA"
    assert mf["part4_modules_completed"] == 10
    assert mf["total_parts_completed"] == 4
    assert mf["total_subsystems"] == 48
    assert mf["overall_test_pass_rate_pct"] == 100.0
    assert mf["security_posture_score"] >= 99.0


def test_delivery_subsystems_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/delivery/subsystems",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_subsystems"] >= 20
    parts = [s["part"] for s in data["subsystems"]]
    assert "Part 1" in parts
    assert "Part 2" in parts
    assert "Part 3" in parts
    assert "Part 4" in parts


def test_delivery_demo_data_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/delivery/demo-data",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_datasets"] >= 3
    domains = [d["domain"] for d in data["datasets"]]
    assert "Financial" in domains
    assert "Cybersecurity" in domains


def test_delivery_packaging_files_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    license_file = repo_root / "LICENSE"
    release_notes_file = repo_root / "RELEASE_NOTES.md"
    readme_file = repo_root / "README.md"
    demo_data_file = repo_root / "data" / "demo_enterprise_datasets.json"

    assert license_file.exists()
    assert release_notes_file.exists()
    assert readme_file.exists()
    assert demo_data_file.exists()

    # Content assertions
    license_content = license_file.read_text(encoding="utf-8")
    assert "Apache License" in license_content
    assert "Version 2.0" in license_content

    rn_content = release_notes_file.read_text(encoding="utf-8")
    assert "Official Release Notes" in rn_content
    assert "v1.0.0-GA" in rn_content

    readme_content = readme_file.read_text(encoding="utf-8")
    assert "AegisIQ" in readme_content
    assert "Quick Start" in readme_content

    demo_content = demo_data_file.read_text(encoding="utf-8")
    assert "DS-FIN-001" in demo_content
    assert "DS-CHURN-002" in demo_content
