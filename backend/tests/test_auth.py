def test_system_health(client):
    """Test system health check endpoint."""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"


def test_seed_admin_login(client):
    """Test authentication with seeded enterprise admin account."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "admin@aegisiq.com"
    assert any(role["name"] == "Admin" for role in data["user"]["roles"])


def test_invalid_login_credentials(client):
    """Test login failure with bad password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_register_new_user(client):
    """Test new user registration with assigned role."""
    new_user_payload = {
        "email": "test.analyst@aegisiq.com",
        "password": "SecurePassword@123",
        "full_name": "Sarah Connor",
        "job_title": "Risk Analyst",
        "department": "Risk Intelligence",
        "role_name": "Business Analyst",
    }
    response = client.post("/api/v1/auth/register", json=new_user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test.analyst@aegisiq.com"
    assert any(role["name"] == "Business Analyst" for role in data["user"]["roles"])


def test_register_duplicate_email(client):
    """Test duplicate email rejection."""
    payload = {
        "email": "admin@aegisiq.com",
        "password": "Password123!",
        "full_name": "Duplicate Admin",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_current_user_profile(client):
    """Test protected profile endpoint using JWT Bearer token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "executive@aegisiq.com", "password": "Exec@12345"},
    )
    token = login_res.json()["access_token"]

    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == "executive@aegisiq.com"


def test_rbac_admin_route_authorization(client):
    """Test RBAC: Admin can access admin-only endpoint, Viewer is forbidden."""
    # 1. Login as Admin
    admin_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
    )
    admin_token = admin_res.json()["access_token"]

    res_admin = client.get(
        "/api/v1/auth/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["status"] == "success"

    # 2. Login as Viewer
    viewer_res = client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@aegisiq.com", "password": "Viewer@12345"},
    )
    viewer_token = viewer_res.json()["access_token"]

    res_viewer = client.get(
        "/api/v1/auth/test-rbac/admin-only",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res_viewer.status_code == 403
    assert "Access denied" in res_viewer.json()["detail"]


def test_refresh_token_lifecycle(client):
    """Test refreshing an access token using a refresh token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
    )
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_forgot_and_reset_password_flow(client):
    """Test password reset token generation and execution."""
    forgot_res = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "test.analyst@aegisiq.com"},
    )
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json().get("reset_token")
    assert reset_token is not None

    reset_res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewSecretDataPassword@2026"},
    )
    assert reset_res.status_code == 200

    # Login with new password
    new_login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "test.analyst@aegisiq.com", "password": "NewSecretDataPassword@2026"},
    )
    assert new_login_res.status_code == 200



def test_audit_logs_tracking(client):
    """Test that authentication events generate audit logs."""
    admin_res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegisiq.com", "password": "Admin@12345"},
    )
    admin_token = admin_res.json()["access_token"]

    logs_res = client.get(
        "/api/v1/auth/activity-logs?limit=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0
    assert any("LOGIN" in log["action"] or "SEED" in log["action"] for log in logs)
