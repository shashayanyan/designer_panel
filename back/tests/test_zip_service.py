import zipfile
import json
import io
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_generate_package_returns_valid_zip():
    """
    Simulates sending a request to /api/v1/engine/generate-package.
    Verifies the response structure is a valid ZIP file and contains
    the expected manifest, neutral, and docs files.
    """
    request_payload = {
        "series_id": "TEST_SR",
        "motor_power_kw": 10.0,
        "load_count": 2,
        "ats_included": False,
        "selected_assets": ["Data Sheet", "Bill of Materials", "Specification"]
    }
    
    response = client.post("/api/v1/engine/generate-package", json=request_payload)
    
    # Assert successful generation
    assert response.status_code == 200, f"Endpoint failed: {response.text}"
    assert response.headers["content-type"] == "application/x-zip-compressed"
    
    # Load byte stream into python's native ZipFile library
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        # Get list of all file names inside the archive
        file_list = zf.namelist()
        
        # 1. Assert Manifest exists at root
        assert "manifest.json" in file_list
        
        # 2. Assert manifest is legitimate JSON with expected keys
        manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
        assert manifest_data["series"] == "TEST_SR"
        config_id = manifest_data["config_id"]
        
        # 3. Assert Sub-Directories and files exist exactly as architected
        json_path = f"Neutral/DigitalTwin_DNA_{config_id}.json"
        excel_path = f"Neutral/ApplicationPack_{config_id}.xlsx"
        word_path = f"EngineeringSpec_{config_id}.docx"
        
        assert json_path in file_list
        assert excel_path in file_list
        assert word_path in file_list
        
        # 4. Light verification of JSON twin extraction
        extracted_twin = json.loads(zf.read(json_path).decode("utf-8"))
        assert extracted_twin["load_count"] == 2
        assert extracted_twin["series_id"] == "TEST_SR"
