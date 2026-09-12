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


def test_docs_overview_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/docs/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    ov = data["overview"]
    assert ov["total_documents"] >= 5
    doc_titles = [d["title"] for d in ov["documents"]]
    assert any("SRS" in t for t in doc_titles)
    assert any("HLD" in t for t in doc_titles)
    assert any("LLD" in t for t in doc_titles)


def test_architecture_layers_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/docs/architecture",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_layers"] >= 5
    layer_names = [l["layer_name"] for l in data["layers"]]
    assert any("Client" in name for name in layer_names)
    assert any("Security" in name for name in layer_names)
    assert any("Observability" in name for name in layer_names)


def test_incident_playbooks_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/docs/runbook-topics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_playbooks"] >= 3
    alert_names = [p["alert_name"] for p in data["playbooks"]]
    assert "HighHttpErrorRate" in alert_names
    assert "ElevatedApiLatencyP99" in alert_names


def test_documentation_markdown_files_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    srs_file = repo_root / "docs" / "SRS.md"
    hld_file = repo_root / "docs" / "HLD.md"
    lld_file = repo_root / "docs" / "LLD.md"
    deploy_file = repo_root / "docs" / "DEPLOYMENT_GUIDE.md"
    runbook_file = repo_root / "docs" / "ADMIN_RUNBOOK.md"

    assert srs_file.exists()
    assert hld_file.exists()
    assert lld_file.exists()
    assert deploy_file.exists()
    assert runbook_file.exists()

    # Content assertions
    srs_content = srs_file.read_text(encoding="utf-8")
    assert "Software Requirements Specification" in srs_content
    assert "5-Tier Role-Based Access Control" in srs_content

    hld_content = hld_file.read_text(encoding="utf-8")
    assert "High-Level Design" in hld_content
    assert "mermaid" in hld_content

    lld_content = lld_file.read_text(encoding="utf-8")
    assert "Low-Level Design" in lld_content
    assert "TreeSHAP" in lld_content

    deploy_content = deploy_file.read_text(encoding="utf-8")
    assert "Production Deployment Guide" in deploy_content
    assert "docker compose" in deploy_content

    runbook_content = runbook_file.read_text(encoding="utf-8")
    assert "Operational Runbook" in runbook_content
    assert "Playbook 1: Alert" in runbook_content
