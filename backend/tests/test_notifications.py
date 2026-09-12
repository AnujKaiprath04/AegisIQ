import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_notifications_and_unread_count(client: TestClient):
    token = get_auth_token(client)
    
    # 1. List notifications
    res = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 3
    assert any(i["category"] == "SECURITY" for i in items)

    # 2. Check unread count
    count_res = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert count_res.status_code == 200
    assert count_res.json()["unread_count"] >= 1


def test_mark_notification_as_read(client: TestClient):
    token = get_auth_token(client)
    
    # Get first unread
    res = client.get("/api/v1/notifications?unread_only=true", headers={"Authorization": f"Bearer {token}"})
    unread_items = res.json()
    if unread_items:
        target_id = unread_items[0]["id"]
        read_res = client.post(
            f"/api/v1/notifications/{target_id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] is True


def test_mark_all_notifications_read(client: TestClient):
    token = get_auth_token(client)
    
    res = client.post(
        "/api/v1/notifications/mark-all-read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert "marked as read" in res.json()["message"]

    # Verify unread count is now 0
    count_res = client.get("/api/v1/notifications/unread-count", headers={"Authorization": f"Bearer {token}"})
    assert count_res.json()["unread_count"] == 0


def test_alert_rules_lifecycle_and_toggle(client: TestClient):
    token = get_auth_token(client)
    
    # 1. Create alert rule
    rule_payload = {
        "name": "Custom High-Risk Churn Alert",
        "trigger_event": "HIGH_CHURN_RISK",
        "threshold_condition": "Churn Probability >= 80%",
        "severity": "CRITICAL",
        "channel_in_app": True,
        "channel_email": True,
        "channel_webhook": True,
        "webhook_url": "https://hooks.slack.com/services/T00/B00/ZZZ",
    }
    create_res = client.post(
        "/api/v1/notifications/rules",
        json=rule_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    rule_id = create_res.json()["id"]
    assert create_res.json()["is_active"] is True

    # 2. Toggle alert rule
    toggle_res = client.post(
        f"/api/v1/notifications/rules/{rule_id}/toggle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False


def test_webhook_test_dispatch(client: TestClient):
    token = get_auth_token(client)
    
    dispatch_payload = {
        "webhook_url": "https://hooks.slack.com/services/T123/B456/7890",
        "channel_name": "Executive Incident Broadcast",
    }
    res = client.post(
        "/api/v1/notifications/webhook/test",
        json=dispatch_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["response_status_code"] == 200
    assert data["latency_ms"] > 0
