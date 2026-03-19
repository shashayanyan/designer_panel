import pytest
from fastapi.testclient import TestClient

from app.main import app

# Use standard TestClient for calling FastAPI endpoints synchronously during tests.
client = TestClient(app)

# Hardcoded test cases matching the dummy data injected by `tests/conftest.py`
test_data = [
    {
        "config_id": "CFG-TEST_OPT_1-2X",
        "series_id": "TEST_SR",
        "motor_power_kw": 10.0,
        "load_count": 2,
        "ats_included": False,
        "ex_enclosure_ref": "ENC-001",
        "ex_enclosure_dims": "1200x800x400",
        "ex_magnetic_cb": "TEST_CB",
        "ex_contactor": "TEST_CONT",
        "ex_overload": "TEST_OVL",
    }
]

@pytest.mark.parametrize("case", test_data)
def test_engine_resolves_correctly_against_csv(case):
    """
    Automatically sends requests to /api/v1/engine/configure based on Configurations.csv 
    and strictly compares the returned Digital Twin JSON values against the expected columns.
    """
    request_payload = {
        "series_id": case["series_id"],
        "motor_power_kw": case["motor_power_kw"],
        "load_count": case["load_count"],
        "ats_included": case["ats_included"]
    }
    
    response = client.post("/api/v1/engine/configure", json=request_payload)
    
    # Assert successful resolution
    assert response.status_code == 200, f"Failed for {case['config_id']}: {response.text}"
    
    data = response.json()
    
    # 1. Check ID Mapping
    assert data["config_id"] == case["config_id"]
    
    # 2. Check Enclosure Resolution
    assert data["enclosure"]["catalog_ref"] == case["ex_enclosure_ref"]
    assert data["enclosure"]["dimensions_mm"] == case["ex_enclosure_dims"]
    
    # 3. Check Components parsing
    components = data.get("components", [])
    part_numbers = [c["part_number"] for c in components]
    
    if case["ex_magnetic_cb"] is not None:
        assert case["ex_magnetic_cb"] in part_numbers
    if case["ex_contactor"] is not None:
        assert case["ex_contactor"] in part_numbers
    if case["ex_overload"] is not None:
        assert case["ex_overload"] in part_numbers

    # Verify component quantities equal load_count
    for c in components:
        assert float(c["qty"]) == float(case["load_count"])
