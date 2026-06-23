from pathlib import Path
from types import SimpleNamespace

import pytest

from app.generators import bim_gen


class FakeEntity(SimpleNamespace):
    def __init__(self, **kwargs):
        kwargs.setdefault("FlowDirection", None)
        kwargs.setdefault("PredefinedType", None)
        super().__init__(**kwargs)


class FakeRepresentation(SimpleNamespace):
    pass


class FakeModel:
    def __init__(self):
        self.written = []

    def to_string(self):
        return "IFC-DATA"


@pytest.fixture
def fake_ifcopenshell(monkeypatch):
    model = FakeModel()
    calls = SimpleNamespace(
        ports=[],
        styles=[],
        psets=[],
        placements=[],
        created=[],
        clearances=[],
    )

    def create_file(version):
        assert version == "IFC4"
        return model

    def create_entity(_model, ifc_class, name):
        entity = FakeEntity(ifc_class=ifc_class, name=name)
        calls.created.append(entity)
        return entity

    def add_context(_model, **kwargs):
        return SimpleNamespace(**kwargs)

    def add_mesh_representation(_model, **kwargs):
        return FakeRepresentation(Items=[FakeEntity(name="mesh-item")], **kwargs)

    def add_style(_model, name):
        return FakeEntity(name=name)

    def add_surface_style(_model, **kwargs):
        return None

    def assign_item_style(_model, item, style):
        calls.styles.append((item, style))

    def add_pset(_model, product, name):
        pset = FakeEntity(name=name, properties={})
        calls.psets.append((product, pset))
        return pset

    def edit_pset(_model, pset, properties):
        pset.properties = properties

    def assign_representation(_model, product, representation):
        product.representation = representation

    def edit_object_placement(_model, product, matrix):
        calls.placements.append((product, matrix))

    def assign_object(_model, **kwargs):
        return None

    def assign_container(_model, **kwargs):
        return None

    def assign_port(_model, element, port):
        calls.ports.append((element, port))

    def assign_type(_model, **kwargs):
        return None

    monkeypatch.setattr(bim_gen.ifcopenshell.api.project, "create_file", create_file)
    monkeypatch.setattr(bim_gen.ifcopenshell.api.root, "create_entity", create_entity)
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.unit, "assign_unit", lambda _model: None
    )
    monkeypatch.setattr(bim_gen.ifcopenshell.api.context, "add_context", add_context)
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.geometry,
        "add_mesh_representation",
        add_mesh_representation,
    )
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.geometry,
        "assign_representation",
        assign_representation,
    )
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.geometry,
        "edit_object_placement",
        edit_object_placement,
    )
    monkeypatch.setattr(bim_gen.ifcopenshell.api.style, "add_style", add_style)
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.style, "add_surface_style", add_surface_style
    )
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.style, "assign_item_style", assign_item_style
    )
    monkeypatch.setattr(bim_gen.ifcopenshell.api.pset, "add_pset", add_pset)
    monkeypatch.setattr(bim_gen.ifcopenshell.api.pset, "edit_pset", edit_pset)
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.aggregate, "assign_object", assign_object
    )
    monkeypatch.setattr(
        bim_gen.ifcopenshell.api.spatial, "assign_container", assign_container
    )
    monkeypatch.setattr(bim_gen.ifcopenshell.api.system, "assign_port", assign_port)
    monkeypatch.setattr(bim_gen.ifcopenshell.api.type, "assign_type", assign_type)

    return model, calls


def test_basic_helpers_and_port_creation(fake_ifcopenshell, tmp_path):
    model, calls = fake_ifcopenshell

    assert bim_gen.mm_to_m(2500) == 2.5

    style = bim_gen.create_color_style(model, "TestStyle", 0.1, 0.2, 0.3)
    representation = bim_gen.create_box_representation(model, "ctx", 1.0, 2.0, 3.0)
    panel = FakeEntity(name="Panel")

    bim_gen.assign_representation(model, panel, representation)
    bim_gen.create_port(
        model, "ctx", panel, "Port_A", "SOURCE", 1, 2, 3, visualize=False
    )
    bim_gen.create_port(
        model,
        "ctx",
        panel,
        "Port_B",
        "SINK",
        4,
        5,
        6,
        visualize=True,
        color_style=style,
    )
    bim_gen.create_clearance_zone(model, "ctx", panel, "Zone", 1, 2, 3, 4, 5, 6, style)

    component = bim_gen.create_subcomponent(
        model,
        "ctx",
        panel,
        {
            "part_number": "T-001",
            "item_category": "Control Terminal",
            "description": "Terminal block",
            "item": "TB1",
        },
        1,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        style,
    )

    data_file = tmp_path / "sample.json"
    data_file.write_text('{"ok": true}', encoding="utf-8")

    assert data_file.exists()
    assert panel.representation is representation
    assert component.Description == "Terminal block"
    assert calls.psets[-1][1].properties["Manufacturer"] == "Schneider Electric"
    assert len(calls.ports) == 2
    assert calls.ports[0][1].FlowDirection == "SOURCE"
    assert calls.ports[1][1].FlowDirection == "SINK"
    assert len(calls.styles) >= 1


def test_generate_ifc_from_twin_covers_branching(fake_ifcopenshell):
    model, calls = fake_ifcopenshell
    data = {
        "config_id": "CFG-1",
        "series_id": "SS",
        "motor_power_kw": 15,
        "load_count": 2,
        "communication": "ModbusTCP",
        "notes": "Generator coverage test",
        "enclosure": {
            "catalog_ref": "ENC-001",
            "dimensions_mm": "1200x800x400",
        },
        "components": [
            {
                "part_number": "CORE-1",
                "item_category": "Core Device",
            }
        ],
        "bom_lines": [
            {"item_category": "Enclosure", "qty": "1"},
            {
                "item_category": "Start PB",
                "qty": "1",
                "part_number": "PB-1",
                "description": "Start push button",
                "item": "PB",
            },
            {
                "item_category": "Control Terminal",
                "qty": "2",
                "part_number": "T-2",
                "description": "Terminal",
                "item": "TERM",
            },
            {
                "item_category": "Power Cable Gland",
                "qty": "1",
                "part_number": "G-1",
                "description": "Cable gland",
                "item": "GLAND",
            },
            {
                "item_category": "Core Device",
                "qty": "1",
                "part_number": "C-1",
                "description": "Core device",
                "item": "CORE",
            },
        ],
    }

    output = bim_gen.generate_ifc_from_twin(data, visualize_ports=True)

    assert output == b"IFC-DATA"
    assert model.to_string() == "IFC-DATA"
    assert len(calls.created) > 0
    assert len(calls.ports) == 4


def test_load_data_and_main_write_output(monkeypatch, tmp_path):
    sample = tmp_path / "input.json"
    sample.write_text('{"config_id": "CFG-2"}', encoding="utf-8")

    assert bim_gen.load_data(str(sample)) == {"config_id": "CFG-2"}

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(bim_gen, "load_data", lambda _path: {"config_id": "CFG-2"})
    monkeypatch.setattr(
        bim_gen, "generate_ifc_from_twin", lambda _data, visualize_ports=False: b"IFC"
    )
    monkeypatch.setattr(
        bim_gen.argparse,
        "ArgumentParser",
        lambda *args, **kwargs: SimpleNamespace(
            add_argument=lambda *a, **k: None,
            parse_args=lambda: SimpleNamespace(
                visualize_ports=True, output_name="panel"
            ),
        ),
    )

    bim_gen.main()

    assert Path("panel_Visual.ifc").exists()
