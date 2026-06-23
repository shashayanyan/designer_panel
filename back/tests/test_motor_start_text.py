from app.main import app
from fastapi.testclient import TestClient

from test_zip_service import auth_headers

client = TestClient(app)


def test_get_dol_motor_start_text_success():
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


def test_get_ss_11_motor_start_text_success():
    response = client.get(
        "/api/v1/motor-start-text/2/SS/11.0/ENC-002",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "description" in data
    assert "technical_characteristics" in data
    assert "functions" in data
    assert "protections" in data
    assert "2 independent pump feeders" in data["technical_characteristics"]
    assert "altistart 01" in data["technical_characteristics"].lower()


def test_get_ss_22_motor_start_text_success():
    response = client.get(
        "/api/v1/motor-start-text/2/SS/22.0/ENC-002",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "description" in data
    assert "technical_characteristics" in data
    assert "functions" in data
    assert "protections" in data
    assert "2 independent pump feeders" in data["technical_characteristics"]
    assert "ats130" in data["description"].lower()


def test_get_vsd_motor_start_text_success():
    response = client.get(
        "/api/v1/motor-start-text/4/VSD/22.0/ENC-003",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "description" in data
    assert "technical_characteristics" in data
    assert "functions" in data
    assert "protections" in data
    assert "4 independent pump drives" in data["technical_characteristics"]
    assert "variable speed drive" in data["description"].lower()


def test_get_default_to_ss_motor_start_text():
    response = client.get(
        "/api/v1/motor-start-text/4/UNKNOWN/22.0/ENC-004",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "description" in data
    assert "technical_characteristics" in data
    assert "functions" in data
    assert "protections" in data
    assert "4 independent pump feeders" in data["technical_characteristics"]
    assert "soft starter" in data["description"].lower()
