from app.main import app
from fastapi.testclient import TestClient

from test_zip_service import auth_headers

client = TestClient(app)


def test_get_motor_start_text_success():
    response = client.get(
        "/api/v1/motor-start-text/3/DOL/15.0/ENC-001",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "description" in data
    assert "technical_characteristics" in data
    assert "functions" in data
    assert "protections" in data
    assert "3 independent pump feeders" in data["technical_characteristics"]
