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


def test_observability_overview_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/observability/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    ov = data["overview"]
    assert "ONLINE" in ov["apm_status"]
    assert ov["total_metrics_tracked"] >= 5
    metric_names = [m["name"] for m in ov["metrics"]]
    assert "http_requests_total" in metric_names
    assert "pg_stat_activity_count" in metric_names
    assert "aegisiq_model_psi_score" in metric_names


def test_alertmanager_rules_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/observability/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rules"] >= 4
    rule_names = [r["name"] for r in data["rules"]]
    assert "HighHttpErrorRate" in rule_names
    assert "ElevatedApiLatencyP99" in rule_names
    assert "PostgresConnectionPoolHigh" in rule_names
    assert "ModelPredictionDriftAnomaly" in rule_names


def test_structured_log_streaming_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ops/observability/logs?limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_logs"] > 0
    first_log = data["logs"][0]
    assert "trace_id" in first_log
    assert "span_id" in first_log
    assert first_log["level"] in ["INFO", "WARNING", "ERROR"]


def test_monitoring_manifest_files_exist():
    # Base repo path: c:/Work to do/FYP
    repo_root = Path(__file__).resolve().parent.parent.parent

    prom_yml = repo_root / "monitoring" / "prometheus.yml"
    alert_yml = repo_root / "monitoring" / "alertmanager" / "alert_rules.yml"
    grafana_json = repo_root / "monitoring" / "grafana" / "dashboards" / "aegisiq-overview.json"
    loki_yml = repo_root / "monitoring" / "loki" / "loki-config.yml"
    promtail_yml = repo_root / "monitoring" / "promtail" / "promtail-config.yml"

    assert prom_yml.exists()
    assert alert_yml.exists()
    assert grafana_json.exists()
    assert loki_yml.exists()
    assert promtail_yml.exists()

    # Content assertions
    prom_content = prom_yml.read_text(encoding="utf-8")
    assert "aegisiq-backend" in prom_content
    assert "/metrics" in prom_content

    alert_content = alert_yml.read_text(encoding="utf-8")
    assert "HighHttpErrorRate" in alert_content
    assert "ModelPredictionDriftAnomaly" in alert_content

    grafana_content = grafana_json.read_text(encoding="utf-8")
    assert "AegisIQ Enterprise Executive Telemetry" in grafana_content
