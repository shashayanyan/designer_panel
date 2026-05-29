import io
import json
import zipfile

from app import models
from app.auth import create_access_token
from app.database import get_db
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def auth_headers(username="testuser"):
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


def extract_config_id(response):
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        manifest = json.loads(zf.read("001_manifest.json").decode("utf-8"))
    return manifest["config_id"]


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


def test_generate_package_persists_project_metadata_for_authenticated_user():
    request_payload = {
        "series_id": "DOL",
        "motor_power_kw": 10.0,
        "load_count": 2,
        "ats_included": False,
        "plc_included": "YES",
        "scada_included": "No",
        "selected_assets": [],
        "project_name": "Metadata Project",
        "project_client": "ACME Corp",
        "project_technical_manager": "Eng Lead",
        "project_location": "Test Site",
        "project_date": "2026-05-28",
        "project_notes": "Store me",
    }

    response = client.post(
        "/api/v1/engine/generate-package",
        json=request_payload,
        headers=auth_headers(),
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/x-zip-compressed"

    config_id = extract_config_id(response)

    db = next(app.dependency_overrides[get_db]())
    metadata = (
        db.query(models.ProjectMetadata)
        .filter(models.ProjectMetadata.config_id == config_id)
        .first()
    )

    assert metadata is not None
    assert metadata.username == "testuser"
    assert metadata.project_name == "Metadata Project"
    assert metadata.client == "ACME Corp"
    assert metadata.technical_manager == "Eng Lead"
    assert metadata.location == "Test Site"
    assert metadata.date == "2026-05-28"
    assert metadata.notes == "Store me"
    assert metadata.plc is True
    assert metadata.scada is False

    db.close()
