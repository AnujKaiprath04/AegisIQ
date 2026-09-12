import pytest
from fastapi.testclient import TestClient


def get_auth_token(client: TestClient, email: str, password: str = "Admin@12345") -> str:
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_admin_list_users(client: TestClient):
    admin_token = get_auth_token(client, "admin@aegisiq.com")
    res = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "users" in data
    assert data["total_count"] >= 5


def test_non_admin_cannot_list_users(client: TestClient):
    viewer_token = get_auth_token(client, "viewer@aegisiq.com", "Viewer@12345")
    res = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403


def test_admin_create_and_update_user(client: TestClient):
    admin_token = get_auth_token(client, "admin@aegisiq.com")
    new_user_payload = {
        "email": "test.user.new@aegisiq.com",
        "password": "SecurePassword@123",
        "full_name": "Test Engineer New",
        "job_title": "Platform Tester",
        "department": "Engineering",
        "role_name": "Data Analyst",
        "is_active": True,
    }
    create_res = client.post(
        "/api/v1/users",
        json=new_user_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["email"] == "test.user.new@aegisiq.com"
    user_id = created["id"]

    # Update User
    update_payload = {
        "job_title": "Lead Platform Tester",
        "department": "Core Platform",
    }
    update_res = client.put(
        f"/api/v1/users/{user_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["job_title"] == "Lead Platform Tester"
    assert updated["department"] == "Core Platform"

    # Delete User
    del_res = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert del_res.status_code == 200
