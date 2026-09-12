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


def test_get_cicd_pipeline_runs(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/cicd/runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_runs"] >= 2
    run = data["runs"][0]
    assert run["status"] == "SUCCESS"
    assert len(run["jobs"]) >= 4


def test_get_deployment_releases(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/cicd/releases",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_releases"] >= 2
    release = next(r for r in data["releases"] if r["is_active"])
    assert release["release_tag"] == "v1.0.0"
    assert "sha256:" in release["docker_digest"]


def test_trigger_rollback_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ops/cicd/rollback",
        json={
            "target_tag": "v0.9.8-rc2",
            "reason": "Test automated healthcheck regression rollback",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    result = data["result"]
    assert result["status"] == "ROLLBACK_EXECUTED_SUCCESSFULLY"
    assert result["restored_tag"] == "v0.9.8-rc2"
    assert result["health_check_passed"] is True


def test_github_actions_workflows_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    workflows_dir = repo_root / ".github" / "workflows"
    ci_yml = workflows_dir / "ci.yml"
    security_yml = workflows_dir / "security-scan.yml"
    cd_yml = workflows_dir / "cd-deploy.yml"
    rollback_yml = workflows_dir / "rollback.yml"

    assert ci_yml.exists()
    assert security_yml.exists()
    assert cd_yml.exists()
    assert rollback_yml.exists()

    # Verify content keywords
    ci_content = ci_yml.read_text(encoding="utf-8")
    assert "backend-ci" in ci_content
    assert "frontend-ci" in ci_content

    sec_content = security_yml.read_text(encoding="utf-8")
    assert "trivy-scan" in sec_content
    assert "bandit" in sec_content

    cd_content = cd_yml.read_text(encoding="utf-8")
    assert "ghcr.io" in cd_content
    assert "docker/build-push-action" in cd_content

    rb_content = rollback_yml.read_text(encoding="utf-8")
    assert "rollback-deployment" in rb_content
