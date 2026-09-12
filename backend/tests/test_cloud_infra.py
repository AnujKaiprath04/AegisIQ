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


def test_cloud_topology_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/infra/cloud/topology",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    top = data["topology"]
    assert "Vercel" in top["frontend_provider"]
    assert "Render" in top["backend_provider"]
    assert top["database_info"]["provider"] == "NEON_POSTGRES"
    assert top["k8s_ready"] is True
    assert len(top["storage_buckets"]) >= 4


def test_cloud_storage_status(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/infra/cloud/storage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_buckets"] >= 4
    bucket_ids = [b["bucket_id"] for b in data["buckets"]]
    assert "aegisiq-datasets" in bucket_ids
    assert "aegisiq-ml-artifacts" in bucket_ids
    assert "aegisiq-reports" in bucket_ids
    assert "aegisiq-backups" in bucket_ids


def test_cloud_database_status(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/infra/cloud/database",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    db = data["database"]
    assert db["provider"] == "NEON_POSTGRES"
    assert db["ssl_enforced"] is True
    assert "PgBouncer" in db["pooling_driver"]


def test_cloud_manifests_and_k8s_files_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    # 1. Cloud manifests
    vercel_json = repo_root / "vercel.json"
    render_yaml = repo_root / "render.yaml"
    neon_sql = repo_root / "deployment" / "neon_db_setup.sql"
    supabase_sql = repo_root / "deployment" / "supabase_storage.sql"

    assert vercel_json.exists()
    assert render_yaml.exists()
    assert neon_sql.exists()
    assert supabase_sql.exists()

    # 2. Kubernetes manifests
    k8s_dir = repo_root / "deployment" / "k8s"
    assert (k8s_dir / "namespace.yaml").exists()
    assert (k8s_dir / "configmap.yaml").exists()
    assert (k8s_dir / "secrets.yaml").exists()
    assert (k8s_dir / "backend-deployment.yaml").exists()
    assert (k8s_dir / "frontend-deployment.yaml").exists()
    assert (k8s_dir / "ingress.yaml").exists()

    # 3. Content assertions
    vercel_content = vercel_json.read_text(encoding="utf-8")
    assert "rewrites" in vercel_content
    assert "X-Frame-Options" in vercel_content

    render_content = render_yaml.read_text(encoding="utf-8")
    assert "aegisiq-backend" in render_content
    assert "healthCheckPath" in render_content

    neon_content = neon_sql.read_text(encoding="utf-8")
    assert "aegisiq_core" in neon_content

    backend_k8s = (k8s_dir / "backend-deployment.yaml").read_text(encoding="utf-8")
    assert "HorizontalPodAutoscaler" in backend_k8s
    assert "runAsNonRoot: true" in backend_k8s
