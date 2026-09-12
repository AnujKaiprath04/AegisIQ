import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_alert_rules(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ml/alerts/rules",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_rules"] >= 4
    rule_ids = [r["rule_id"] for r in data["rules"]]
    assert "RULE-CHURN-001" in rule_ids
    assert "RULE-SEC-002" in rule_ids


def test_create_alert_rule(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ml/alerts/rules",
        json={
            "rule_id": "RULE-TEST-009",
            "name": "Custom ARR Downside Alert",
            "trigger_source": "PREDICTION_REVENUE",
            "condition_metric": "arr_downside_usd",
            "threshold": 100000.0,
            "target_channels": ["SLACK", "EMAIL"],
            "escalation_enabled": True,
            "dedup_window_minutes": 20,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["rule_id"] == "RULE-TEST-009"
    assert data["threshold"] == 100000.0


def test_dispatch_alert_success_and_deduplication(client: TestClient):
    token = get_auth_token(client)
    # 1. First Dispatch -> DISPATCHED
    res1 = client.post(
        "/api/v1/ml/alerts/dispatch",
        json={
            "rule_id": "RULE-CHURN-001",
            "title": "Critical Churn Alert: Acme Corporation",
            "description": "Predicted churn probability is 82% ($350k ARR).",
            "severity": "CRITICAL",
            "target_entity": "ACC-ACME-999",
            "trigger_source": "PREDICTION_CHURN",
            "override_channels": ["SLACK", "MICROSOFT_TEAMS", "WEBHOOK"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["incident"]["status"] == "DISPATCHED"
    assert "slack" in data1["incident"]["channel_payloads"]
    assert "teams" in data1["incident"]["channel_payloads"]

    # 2. Immediate Duplicate Dispatch -> SUPPRESSED_DUPLICATE
    res2 = client.post(
        "/api/v1/ml/alerts/dispatch",
        json={
            "rule_id": "RULE-CHURN-001",
            "title": "Critical Churn Alert: Acme Corporation",
            "description": "Predicted churn probability is 82% ($350k ARR).",
            "severity": "CRITICAL",
            "target_entity": "ACC-ACME-999",
            "trigger_source": "PREDICTION_CHURN",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["incident"]["status"] == "SUPPRESSED_DUPLICATE"


def test_acknowledge_and_resolve_incident(client: TestClient):
    token = get_auth_token(client)
    # Acknowledge
    res_ack = client.post(
        "/api/v1/ml/alerts/incidents/alert-inc-001/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_ack.status_code == 200
    assert res_ack.json()["incident"]["status"] == "ACKNOWLEDGED"

    # Resolve
    res_res = client.post(
        "/api/v1/ml/alerts/incidents/alert-inc-001/resolve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_res.status_code == 200
    assert res_res.json()["incident"]["status"] == "RESOLVED"
