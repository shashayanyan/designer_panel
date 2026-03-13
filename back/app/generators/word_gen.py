import io
from docx import Document
from ..schemas.configurator import DigitalTwinResponse

def generate_word_from_twin(twin: DigitalTwinResponse) -> bytes:
    """
    Takes a unified Digital Twin 'DNA' response and translates it into 
    the Engineering Specification Word document programmatically.
    Returns the DOCX file as a raw byte stream (BytesIO).
    """
    doc = Document()
    
    # 1. Main Headers
    doc.add_heading(f"Engineering Specification Document", 0)
    doc.add_paragraph(f"Project Configuration DNA: {twin.config_id}")
    
    # 2. Overview Section
    doc.add_heading("1. Overview", level=1)
    doc.add_paragraph(
        f"This document outlines the standard engineering parameters for a {twin.load_count}-pump "
        f"Water Booster set, rated at {twin.motor_power_kw} kW per motor. The starter series is defined as {twin.series_id}."
    )
    
    # 3. Control Panel & Enclosure
    doc.add_heading("2. Control Panel & Enclosure", level=1)
    doc.add_paragraph(
        f"The control panel shall be housed in an enclosure dimensioned at {twin.enclosure.dimensions_mm} "
        f"with a mounting type of {twin.enclosure.mounting_type}. Default cabinet rating is IP54."
    )
    
    # 4. Key Components BOM Table
    doc.add_heading("3. Key Components BOM", level=1)
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Item'
    hdr_cells[1].text = 'Part Number'
    hdr_cells[2].text = 'Quantity'
    
    # Add components from Twin
    for comp in twin.components:
        row_cells = table.add_row().cells
        row_cells[0].text = comp.item_category
        row_cells[1].text = comp.part_number
        row_cells[2].text = str(comp.qty)
        
    # Add accessories from Twin
    for acc in twin.accessories:
        row_cells = table.add_row().cells
        row_cells[0].text = acc.category or "Accessory"
        row_cells[1].text = acc.part_number
        row_cells[2].text = str(acc.qty)

    # 5. Export to BytesIO
    output = io.BytesIO()
    doc.save(output)
    
    output.seek(0)
    return output.read()
