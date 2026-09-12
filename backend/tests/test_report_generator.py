import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str = "executive@aegisiq.com", password: str = "Exec@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_list_report_templates(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/ai/reports/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) == 4
    types = [t["type"] for t in templates]
    assert "BOARDROOM_QUARTERLY_BRIEF" in types
    assert "FINANCIAL_OPERATIONAL_REVIEW" in types
    assert "CYBERSECURITY_COMPLIANCE_POSTURE" in types
    assert "DATA_PLATFORM_HEALTH_AUDIT" in types


def test_generate_boardroom_report_markdown(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/reports/generate",
        json={
            "report_type": "BOARDROOM_QUARTERLY_BRIEF",
            "period": "Q1 2026",
            "format": "MARKDOWN",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "BOARDROOM_QUARTERLY_BRIEF"
    assert "$24.8M" in data["rendered_content"]
    assert "Executive Summary" in data["rendered_content"]
    assert len(data["sections"]) == 3
    assert len(data["recommendations"]) > 0


def test_generate_security_report_html(client: TestClient):
    token = get_auth_token(client)
    res = client.post(
        "/api/v1/ai/reports/generate",
        json={
            "report_type": "CYBERSECURITY_COMPLIANCE_POSTURE",
            "period": "Q1 2026",
            "format": "HTML",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "<!DOCTYPE html>" in data["rendered_content"]
    assert "Zero-Trust" in data["rendered_content"] or "SIEM" in data["rendered_content"]


def test_report_history_and_retrieval(client: TestClient):
    token = get_auth_token(client)
    
    # 1. List History
    history_res = client.get(
        "/api/v1/ai/reports/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert history_data["total_reports"] > 0
    report_id = history_data["reports"][0]["report_id"]

    # 2. Get Report by ID
    get_res = client.get(
        f"/api/v1/ai/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["report_id"] == report_id
