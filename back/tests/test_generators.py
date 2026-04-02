import io
from decimal import Decimal
import openpyxl
from docx import Document

from app.schemas.configurator import (
    DigitalTwinResponse,
    TwinEnclosure,
    TwinComponent,
    TwinAccessory
)
from app.generators.excel_gen import generate_excel_from_twin
from app.generators.word_gen import generate_word_from_twin

# Create a mock digital twin response for testing
mock_twin = DigitalTwinResponse(
    config_id="CFG-MOCK-3X",
    series_id="VFD",
    motor_power_kw=Decimal("30.0"),
    load_count=3,
    enclosure=TwinEnclosure(
        catalog_ref="NSYSM18840",
        dimensions_mm="1800x800x400",
        mounting_type="Floor standing"
    ),
    components=[
        TwinComponent(part_number="LC1D50", qty=Decimal("3"), item_category="Contactor")
    ],
    accessories=[
        TwinAccessory(part_number="HMIZ", qty=Decimal("1"), category="HMI")
    ]
)

def test_excel_generation_produces_valid_bytes_and_sheets():
    """
    Ensure the `generate_excel_from_twin` outputs a valid dict of openpyxl byte streams
    with the explicitly developed files.
    """
    excel_files = generate_excel_from_twin(mock_twin)
    
    # Assert bytes isn't empty
    assert len(excel_files) > 0
    
    # Assert expected filenames
    assert "005_Parameters.xlsx" in excel_files
    assert "006_BOM-Template.xlsx" in excel_files
    assert "007_IO-List.xlsx" in excel_files
    
    # Assert parameter mapping worked
    wb = openpyxl.load_workbook(io.BytesIO(excel_files["005_Parameters.xlsx"]))
    params_sheet = wb.active # Since there is only one sheet now
    # Check that the config ID was rendered on the 6th row
    assert params_sheet["B7"].value == "CFG-MOCK-3X"

def test_word_generation_produces_valid_bytes_and_replaces_tags():
    """
    Ensure the `generate_word_from_twin` outputs a valid docx byte stream
    that Jinja templating correctly replaced the tags with Twin values.
    """
    word_bytes = generate_word_from_twin(mock_twin)
    
    assert len(word_bytes) > 0
    
    # Load document from bytes
    doc = Document(io.BytesIO(word_bytes))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)

    # Check for Jinja replacements (config_id, load_count, dimensions)
    rendered_str = "\n".join(full_text)
    
    assert "CFG-MOCK-3X" in rendered_str
    assert "3-pump" in rendered_str
    assert "30.0 kW" in rendered_str
    assert "1800x800x400" in rendered_str
    
    # Ensure raw jinja tags are gone
    assert "{{ config_id }}" not in rendered_str
