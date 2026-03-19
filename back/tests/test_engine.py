import pytest
from fastapi.testclient import TestClient
import pandas as pd
from decimal import Decimal
import os

from app.main import app
from app.database import engine, SessionLocal
from app import models

# Use standard TestClient for calling FastAPI endpoints synchronously during tests.
client = TestClient(app)

# Load CSV References
CSV_PATH = "dev-resources/sheets/Configurations.csv"

def get_csv_configs():
    if not os.path.exists(CSV_PATH):
        return []
    
    df = pd.read_csv(CSV_PATH)
    test_cases = []
    # Test a few random configurations per series/load to span the test space
    samples = df.sample(min(len(df), 20), random_state=42)
    
    for _, row in samples.iterrows():
        test_cases.append({
            "config_id": row["config_id"],
            "series_id": row["series_id"],
            "motor_power_kw": float(row["rated_load_power_kw"]),
            "load_count": int(row["load_count"]),
            "ats_included": bool(row["ats_included"]) if pd.notnull(row["ats_included"]) else False,
            # Expected Core outputs
            "ex_enclosure_ref": row["selected_enclosure_ref"],
            "ex_enclosure_dims": row["selected_enclosure_layout_dims_mm"],
            "ex_magnetic_cb": row["magnetic_cb_part_number"],
            "ex_contactor": row["contactor_part_number"],
            "ex_overload": row["overload_part_number"],
        })
    return test_cases

test_data = get_csv_configs()

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
    
    if pd.notnull(case["ex_magnetic_cb"]):
        assert case["ex_magnetic_cb"] in part_numbers
    if pd.notnull(case["ex_contactor"]):
        assert case["ex_contactor"] in part_numbers
    if pd.notnull(case["ex_overload"]):
        assert case["ex_overload"] in part_numbers

    # Verify component quantities equal load_count
    for c in components:
        assert float(c["qty"]) == float(case["load_count"])
