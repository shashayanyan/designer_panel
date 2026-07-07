from app.generators.asset_number_gen import generate_asset_numbers
from app.utils.assets import flatten_asset_ids

from ...schemas.configurator import DigitalTwinResponse


def has_asset(name, assets_flat):
    return any(a.lower() == name.lower() for a in assets_flat)


def generate_readme_from_twin(twin: DigitalTwinResponse) -> bytes:
    application_type = "Water Booster Set"
    starter_type = {
        "DOL": "Direct-On-Line",
        "YD": "Star-Delta",
        "VFD": "Variable Speed Drive",
        "VSD": "Variable Speed Drive",
    }.get(twin.series_id, twin.series_id)
    enclosure = (
        f"{twin.enclosure.dimensions_mm} - {twin.enclosure.mounting_type}"
        if twin.enclosure
        else "IP54 floor standing"
    )
    redundancy = twin.bypass_strategy if twin.bypass_strategy else "[TBD-REDUNDANCY]"

    assets_flat = flatten_asset_ids(twin.selected_assets)
    asset_numbers = generate_asset_numbers(assets_flat)
    bullet_point_number = 3
    assets = ""

    if has_asset("Data Sheet", assets_flat):
        data_sheet_text = ""
        if has_asset("Parameters", assets_flat):
            data_sheet_text += f"- {asset_numbers['Parameters']}_Parameters.xlsx "
        if has_asset("BOM", assets_flat):
            data_sheet_text += f"- {asset_numbers['BOM']}_BOM-template.xlsx "
        if has_asset("IO", assets_flat):
            data_sheet_text += f"- {asset_numbers['IO']}_IO-List.xlsx "
        if has_asset("Network", assets_flat):
            data_sheet_text += f"- {asset_numbers['Network']}_Network-IP-Plan.xlsx "
        if has_asset("Alarms", assets_flat):
            data_sheet_text += f"- {asset_numbers['Alarms']}_Alarm_List.xlsx "
        assets += f"{bullet_point_number}) {data_sheet_text}\n - Extracted data sheets and templates \n"
        bullet_point_number += 1
    if has_asset("Multi Line Diagram", assets_flat):
        assets += f"{bullet_point_number}) {asset_numbers['MLD-svg']}_MultiLineDiagram.svg / .png, {asset_numbers['RefArch']}_ReferenceArchitecture.png\n   - Generated Multi Line and Reference Architecture diagrams\n"
        bullet_point_number += 1
    if has_asset("Specification", assets_flat):
        assets += f"{bullet_point_number}) {asset_numbers['spec-docx']}_EngineeringSpec_{twin.config_id}.docx, {asset_numbers['spec-txt']}_SpecTextBlock.txt:\n   - Copy/paste-ready specification appendix (shall language)\n"
        assets += "   - Includes reference architecture and typical multi line figure\n"
        bullet_point_number += 1
    if has_asset("BIM Object", assets_flat):
        assets += f"{bullet_point_number}) BIM/{asset_numbers['BIM-visual']}_Visual_{twin.config_id}.ifc:\n   - BIM Object\n"
        bullet_point_number += 1

    content = f"""{application_type} Asset Pack (Prescribe Together) - v1.0
===================================================

Application
- {application_type}: {twin.load_count} pumps x {twin.motor_power_kw} kW each
- Starter type: {starter_type}
- Redundancy: {redundancy}
- Control: Cascade PID pressure control with staging/de-staging + alternation
- Communications: {twin.communication or "Hardwired"}
- Enclosure: {enclosure}

Purpose
This pack is designed as "copy/paste" material for Design Firms at Concept/FEED and Basic Design.
It provides reusable text, drawings, schedules, and templates to prescribe a complete solution approach.

Pack contents
1) 001_README.txt
   - Package readme and generation meta-data
2) 002_DigitalTwin_DNA_{twin.config_id}.json
   - Full digital twin parameter set
{assets}



How to use (recommended)
- Design Firm: paste the DOCX appendix (or relevant sections) into FEED/basic design documentation.
- System Integrator/Panel Builder: confirm ratings, local standards, short-circuit levels and environment; complete BOM with exact part numbers and develop GA/wiring.

Notes
- Part numbers and selection notes are dynamically sourced from the core equipment catalog based on your load configurations.
- The solution can be extended with optional harmonic mitigation, dv/dt filters, bypass, remote SCADA integration, and additional permissives.
"""

    if has_asset("BIM Object", assets_flat):
        content += """

ABOUT THE BIM EXPORT (.ifc)
--------------------------------------------------------------------------------

This configurator application generates Digital Twin BIM models using the IFC4 (Industry Foundation Classes) schema.

Why IFC? We utilize IFC because it is the global, vendor-neutral OpenBIM standard. Rather than locking our data into proprietary, closed-ecosystem formats (like native .rfa or .rvt files), IFC ensures that our panels act as a universal Single Source of Truth. Whether your firm uses Autodesk Revit, Graphisoft Archicad, Navisworks, or Solibri, you are guaranteed to receive our standardized spatial dimensions, clearance requirements, and rich engineering metadata (Psets).


ENGINEERING DISCLAIMER
--------------------------------------------------------------------------------

This BIM export is an engineering accelerator, not a replacement for final design validation.

To ensure maximum software performance and adherence to industry standards, this application prioritizes Level of Information (LOI) over Level of Geometry (LOD):

- Geometry: Internal components (contactors, breakers, busbars) are intentionally omitted to prevent model bloat and software crashing. The geometry represents the true modular outer envelope and dedicated spatial zones.
- Clearances: The semi-transparent models bounding the panel represent mandatory PROVISIONFORSPACE keep-out zones for code-compliant door swinging and maintenance access.
- Validation: All provided electrical values, IP/IK ratings, and spatial dimensions must be verified by a licensed professional against the final submittal drawings before construction.


HOW TO VIEW IN AUTODESK REVIT (2024 / 2026)
--------------------------------------------------------------------------------

Revit users often experience translation errors or missing data when attempting to forcefully "Open" modern IFC4 files. To view the generated models correctly with all colors, ports, and Digital Twin metadata intact, you must use the "Link IFC" workflow.

Do NOT use "File > Open > IFC". This attempts to aggressively convert the neutral IFC geometry into native Revit Families, which is a lossy process that often fails on newer schemas.

The Correct Workflow (Link IFC):
By linking the file, Revit treats the model as a protected, high-fidelity reference (similar to an XREF), preserving all standard Property Sets and visual styles perfectly.

1. Open Autodesk Revit and create a New Project (or open your existing coordination model).
2. Navigate to the "Insert" tab on the top ribbon.
3. Click "Link IFC".
4. Browse to the downloaded .ifc file and click "Open".
5. Switch to a 3D View (the "House" icon in the top toolbar).
6. Optional: Set your Viewport Shading to "Consistent Colors" or "Realistic" to view the physical ports and clearance zones.
7. Select the panel and click "Edit Type" in the Properties Palette to view the injected Digital Twin BOM, electrical ratings, and Manufacturer URLs.
"""
    return content.encode("utf-8")
