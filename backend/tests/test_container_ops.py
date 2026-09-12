import os
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


def test_get_container_specs(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/container/spec",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    ov = data["overview"]
    assert ov["total_containers"] >= 5
    service_names = [s["service_name"] for s in ov["services"]]
    assert "aegisiq-backend" in service_names
    assert "aegisiq-frontend" in service_names
    assert "aegisiq-nginx" in service_names
    assert "aegisiq-postgres" in service_names
    assert "aegisiq-redis" in service_names

    # Check non-root UID enforcement
    backend_spec = next(s for s in ov["services"] if s["service_name"] == "aegisiq-backend")
    assert backend_spec["user_uid"] == 10001
    assert backend_spec["user_name"] == "appuser"


def test_container_runtime_health_probe(client: TestClient):
    # Public probe, no auth required
    res = client.get("/api/v1/ops/container/health")
    assert res.status_code == 200
    data = res.json()
    health = data["health"]
    assert "HEALTHY" in health["container_status"]
    assert "PASSING" in health["liveness_probe_status"]
    assert "PASSING" in health["readiness_probe_status"]


def test_docker_manifests_and_dockerignores_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    # 1. Dockerfiles
    backend_df = repo_root / "docker" / "Dockerfile.backend"
    frontend_df = repo_root / "docker" / "Dockerfile.frontend"
    nginx_df = repo_root / "docker" / "Dockerfile.nginx"
    nginx_conf = repo_root / "docker" / "nginx.conf"

    assert backend_df.exists()
    assert frontend_df.exists()
    assert nginx_df.exists()
    assert nginx_conf.exists()

    # 2. Compose files
    compose_dev = repo_root / "docker-compose.yml"
    compose_prod = repo_root / "docker-compose.prod.yml"

    assert compose_dev.exists()
    assert compose_prod.exists()

    # 3. Dockerignores
    backend_ign = repo_root / "backend" / ".dockerignore"
    frontend_ign = repo_root / "frontend" / ".dockerignore"

    assert backend_ign.exists()
    assert frontend_ign.exists()

    # Verify content keywords
    backend_content = backend_df.read_text(encoding="utf-8")
    assert "appuser" in backend_content
    assert "HEALTHCHECK" in backend_content

    frontend_content = frontend_df.read_text(encoding="utf-8")
    assert "nextjs" in frontend_content
    assert "HEALTHCHECK" in frontend_content

    nginx_content = nginx_conf.read_text(encoding="utf-8")
    assert "upstream backend_upstream" in nginx_content
    assert "proxy_pass" in nginx_content
