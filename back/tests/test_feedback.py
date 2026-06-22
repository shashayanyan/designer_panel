from app.main import app
from app.auth import create_access_token
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_feedback_authenticated():
    # Generate token for the test user injected by conftest
    token = create_access_token(data={"sub": "testuser"})

    payload = {
        "category": "Bug",
        "comment": "This is a test feedback comment.",
        "page_url": "/water",
    }

    response = client.post(
        "/api/v1/feedback", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["username"] == "testuser"
    assert data["category"] == "Bug"
    assert data["comment"] == "This is a test feedback comment."
    assert data["page_url"] == "/water"
    assert data["created_at"] is not None


def test_create_feedback_unauthenticated():
    payload = {
        "category": "General",
        "comment": "Anonymous test feedback.",
        "page_url": "/",
    }

    response = client.post("/api/v1/feedback", json=payload)

    assert response.status_code == 401


def test_create_feedback_invalid_payload():
    token = create_access_token(data={"sub": "testuser"})

    # Missing comment
    payload = {"category": "Feature Request", "page_url": "/"}

    response = client.post(
        "/api/v1/feedback", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
