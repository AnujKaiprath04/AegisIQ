import pytest
from fastapi.testclient import TestClient
from app.security_hardening.rate_limiter import EnterpriseTokenBucketRateLimiter


def get_auth_token(client: TestClient, email: str = "admin@aegisiq.com", password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_security_posture_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/security/hardening/posture",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    posture = data["posture"]
    assert posture["posture_score"] >= 95.0
    assert "A+" in posture["compliance_grade"]
    assert posture["owasp_top_10_compliant"] is True
    assert len(posture["active_defense_layers"]) >= 5


def test_security_headers_audit_endpoint(client: TestClient):
    token = get_auth_token(client)
    res = client.get(
        "/api/v1/security/hardening/headers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_headers"] >= 6
    header_names = [h["header_name"] for h in data["headers"]]
    assert "Strict-Transport-Security" in header_names
    assert "X-Content-Type-Options" in header_names
    assert "X-Frame-Options" in header_names
    assert "Content-Security-Policy" in header_names


def test_threat_inspector_sqli_and_xss(client: TestClient):
    token = get_auth_token(client)

    # 1. Test SQL Injection Detection
    res = client.post(
        "/api/v1/security/hardening/inspect",
        json={"payload": "admin' OR 1=1 --"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    sqli = res.json()["inspection"]
    assert sqli["is_threat_detected"] is True
    assert sqli["detected_category"] == "SQL_INJECTION"
    assert "[REDACTED_SQLI_ATTEMPT]" in sqli["sanitized_output"]

    # 2. Test XSS Detection
    res = client.post(
        "/api/v1/security/hardening/inspect",
        json={"payload": "<script>alert('pwned')</script>"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    xss = res.json()["inspection"]
    assert xss["is_threat_detected"] is True
    assert xss["detected_category"] == "CROSS_SITE_SCRIPTING"
    assert "&lt;script&gt;" in xss["sanitized_output"]

    # 3. Test Benign Payload
    res = client.post(
        "/api/v1/security/hardening/inspect",
        json={"payload": "Normal enterprise search query for Q3 financial performance."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    benign = res.json()["inspection"]
    assert benign["is_threat_detected"] is False
    assert benign["detected_category"] == "BENIGN"


def test_token_bucket_rate_limiter_logic():
    client_key = "test-client-192.168.1.50"
    allowed, remaining, limit, reset_sec = EnterpriseTokenBucketRateLimiter.check_rate_limit(client_key, "STANDARD_USER")
    assert allowed is True
    assert remaining < limit
    assert limit == 120


def test_http_response_security_headers_injected(client: TestClient):
    # Verify live HTTP response from root health contains security headers
    res = client.get("/health")
    assert res.status_code == 200
    assert "x-content-type-options" in res.headers
    assert res.headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in res.headers
    assert res.headers["x-frame-options"] == "SAMEORIGIN"
    assert "strict-transport-security" in res.headers
