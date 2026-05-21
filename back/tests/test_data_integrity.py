from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_accessory_quantity_logic_paths():
    """
    Verify that the engine correctly calculates accessory quantities using:
    1. Formula text (load_count + 5)
    2. Qty per feeder (2.0 * load_count)
    3. Qty per panel (1.0)
    """
    res = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 2,
            "ats_included": False,
        },
    )
    assert res.status_code == 200
    data = res.json()
    accessories = data.get("accessories", [])

    # 1. Formula Accessory: load_count(2) + 5 = 7
    formula_acc = next(
        accessory
        for accessory in accessories
        if accessory["part_number"] == "PART_FORMULA"
    )
    assert float(formula_acc["qty"]) == 7.0

    # 2. Feeder Accessory: 2.0 * load_count(2) = 4
    feeder_acc = next(
        accessory
        for accessory in accessories
        if accessory["part_number"] == "PART_FEEDER"
    )
    assert float(feeder_acc["qty"]) == 4.0

    # 3. Panel Accessory: 1.0
    panel_acc = next(
        accessory
        for accessory in accessories
        if accessory["part_number"] == "PART_PANEL"
    )
    assert float(panel_acc["qty"]) == 1.0


def test_bom_line_source_mapping():
    """
    Verify that the engine correctly enriches BOM lines based on their source type.
    """
    res = client.post(
        "/api/v1/engine/configure",
        json={
            "series_id": "DOL",
            "motor_power_kw": 10.0,
            "load_count": 2,
            "ats_included": False,
        },
    )
    assert res.status_code == 200
    data = res.json()
    bom_lines = data.get("bom_lines", [])

    # 1. Enclosure Source (mapped from EnclosureOption)
    enc_line = next(line for line in bom_lines if line["item_category"] == "Enclosure")
    assert "Enclosure" in enc_line["item"]
    # In conftest, we didn't set a description for EnclosureOption, so notes_text might be empty/null

    # 2. Component Source (mapped from ComponentCatalog)
    comp_line = next(line for line in bom_lines if line["part_number"] == "TEST_CB")
    assert comp_line["item"] == "Dummy CB"
    assert "TestCorp" in comp_line["key_selection_notes"]

    # 3. Accessory Source (mapped from AccessoryCatalog)
    acc_line = next(line for line in bom_lines if line["part_number"] == "PART_PANEL")
    assert acc_line["item"] == "Panel Accessory"
    assert "TestCorp" in acc_line["key_selection_notes"]
