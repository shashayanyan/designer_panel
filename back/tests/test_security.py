from datetime import timedelta
from app.main import app
from app.auth import create_access_token
from fastapi.testclient import TestClient

client = TestClient(app)


def test_expired_token_returns_401():
    """
    Verify that an expired JWT token is rejected.
    """
    # Create a token that expired 10 minutes ago
    expired_token = create_access_token(
        data={"sub": "testuser"}, expires_delta=timedelta(minutes=-10)
    )

    response = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_tampered_token_returns_401():
    """
    Verify that a tampered JWT token is rejected.
    """
    valid_token = create_access_token(data={"sub": "testuser"})
    tampered_token = valid_token[:-1] + ("a" if valid_token[-1] != "a" else "b")

    response = client.get("/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert response.status_code == 401


def test_rbac_user_cannot_access_admin_route():
    """
    Verify that a user with 'User' role cannot access admin-only routes.
    """
    # 1. Login as standard user
    login_res = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}
    )
    token = login_res.json()["access_token"]

    # 2. Attempt to access admin-check
    response = client.get(
        "/api/v1/admin-check", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "The user does not have enough privileges" in response.json()["detail"]


def test_rbac_admin_can_access_admin_route():
    """
    Verify that a user with 'Admin' role can access admin-only routes.
    """
    # 1. Login as admin user
    login_res = client.post(
        "/login", data={"username": "adminuser", "password": "adminpass"}
    )
    token = login_res.json()["access_token"]

    # 2. Attempt to access admin-check
    response = client.get(
        "/api/v1/admin-check", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "Admin"


def test_unauthenticated_access_to_master_data():
    """
    Verify that master data routes are now protected.
    """
    response = client.get("/api/v1/series")
    assert response.status_code == 401
