import io
import json
import zipfile

from app.auth import create_access_token
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def auth_headers(username="testuser"):
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


def extract_config_id(response):
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        twin_file = next(
            f for f in zf.namelist() if f.startswith("002_DigitalTwin_DNA_")
        )
        twin_data = json.loads(zf.read(twin_file).decode("utf-8"))
    return twin_data["config_id"]


def test_enclosure_options_returns_structured_labels():
    response = client.get(
        "/api/v1/enclosure-options/2/DOL/10.0",
        headers=auth_headers(),
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data == [
        {
            "reference": "ENC-001",
            "recommendation_type": "Recommended",
            "material": "Steel",
        }
    ]


def test_generate_package_requires_auth():
    response = client.post(
        "/api/v1/engine/generate-package",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 2,
            "ats_included": False,
            "selected_assets": [],
            "project_name": "Unauthorized Project",
        },
    )

    assert response.status_code == 401
