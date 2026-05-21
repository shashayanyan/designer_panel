from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_power_rating_selection_boundary():
    """
    Verify that the engine selects different starters and components
    based on the motor_power_kw boundary (10kW vs 55kW).
    """
    # 1. 10kW Request
    res_10 = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 2,
            "ats_included": False,
        },
    )
    assert res_10.status_code == 200
    data_10 = res_10.json()
    part_numbers_10 = [c["part_number"] for c in data_10["components"]]
    assert "TEST_CB" in part_numbers_10

    # 2. 55kW Request
    res_55 = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 55.0,
            "load_count": 3,
            "ats_included": False,
        },
    )
    assert res_55.status_code == 200
    data_55 = res_55.json()
    part_numbers_55 = [c["part_number"] for c in data_55["components"]]
    assert "LARGE_CB" in part_numbers_55
    assert "TEST_CB" not in part_numbers_55


def test_ats_enclosure_selection_shift():
    """
    Verify that enabling 'ats_included' correctly shifts the enclosure
    selection for the same power and load count.
    """
    # 1. No ATS
    res_no_ats = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 55.0,
            "load_count": 3,
            "ats_included": False,
        },
    )
    assert res_no_ats.json()["enclosure"]["catalog_ref"] == "ENC-LARGE"

    # 2. With ATS
    res_ats = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 55.0,
            "load_count": 3,
            "ats_included": True,
        },
    )
    assert res_ats.json()["enclosure"]["catalog_ref"] == "ENC-ATS"


def test_manual_enclosure_override():
    """
    Verify that providing an explicit 'enclosure_ref' overrides the
    rule-based recommendation.
    """
    res = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 2,
            "ats_included": False,
            "enclosure_ref": "ENC-LARGE",  # Override recommendation (ENC-001)
        },
    )
    assert res.status_code == 200
    assert res.json()["enclosure"]["catalog_ref"] == "ENC-LARGE"


def test_missing_rule_triggers_404():
    """
    Verify that requesting a configuration for which no rule exists (e.g., 5 loads)
    returns a 404 error instead of a crash.
    """
    res = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 5,  # No rule for 5 loads in conftest
            "ats_included": False,
        },
    )
    assert res.status_code == 404
    assert "No matching enclosure configuration rule found" in res.json()["detail"]


def test_missing_starter_triggers_404():
    """
    Verify that requesting a power rating not in the catalog returns a 404.
    """
    res = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 999.0,  # Not in catalog
            "load_count": 2,
            "ats_included": False,
        },
    )
    assert res.status_code == 404
    assert "No matching starter option found" in res.json()["detail"]
