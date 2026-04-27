from app.generators.asset_number_gen import generate_asset_numbers

from ...schemas.configurator import DigitalTwinResponse

def has_asset(name, twin):
            return any(a.lower() == name.lower() for a in twin.selected_assets)

def generate_readme_from_twin(twin: DigitalTwinResponse) -> bytes:
    application_type = "Water Booster Set"
    starter_type = {"DOL": "Direct-On-Line", "YD": "Star-Delta", "VFD": "Variable Speed Drive", "VSD": "Variable Speed Drive"}.get(twin.series_id, twin.series_id)
    enclosure = f"{twin.enclosure.dimensions_mm} - {twin.enclosure.mounting_type}" if twin.enclosure else "IP54 floor standing"
    redundancy = twin.bypass_strategy if twin.bypass_strategy else "[TBD-REDUNDANCY]"
    asset_numbers = generate_asset_numbers(twin.selected_assets or [])
    bullet_point_number = 3
    assets = ""

    if has_asset("Data Sheet", twin):
       assets += f"{bullet_point_number}) {asset_numbers['Parameters']}_Parameters.xlsx, {asset_numbers['BOM']}_BOM-template.xlsx, {asset_numbers['IO']}_IO-List.xlsx, {asset_numbers['Network']}_Network-IP-Plan.xlsx, {asset_numbers['Alarms']}_Alarm_List.xlsx, {asset_numbers['Options']}_Option-Matrix.xlsx\n   - Extracted data sheets and templates\n"
       bullet_point_number += 1
    if has_asset("Multi Line Diagram", twin):
       assets += f"{bullet_point_number}) {asset_numbers['MLD-svg']}_MultiLineDiagram.svg / .png, {asset_numbers['RefArch']}_ReferenceArchitecture.png\n   - Generated Multi Line and Reference Architecture diagrams\n"
       bullet_point_number += 1
    if has_asset("Specification", twin):
       assets += f"{bullet_point_number}) {asset_numbers['spec-docx']}_EngineeringSpec_{twin.config_id}.docx, {asset_numbers['spec-txt']}_SpecTextBlock.txt:\n   - Copy/paste-ready specification appendix (shall language)\n"
       assets += "   - Includes reference architecture and typical multi line figure\n"
       bullet_point_number += 1
    if has_asset("BIM Object", twin):
       assets += f"{bullet_point_number}) BIM/{asset_numbers['BIM-logical']}_Logical_{twin.config_id}.ifc, BIM/{asset_numbers['BIM-visual']}_Visual_{twin.config_id}.ifc:\n   - BIM Object variants\n"
       bullet_point_number += 1



    content = f"""{application_type} Asset Pack (Prescribe Together) - v1.0
===================================================

Application
- {application_type}: {twin.load_count} pumps x {twin.motor_power_kw} kW each
- Starter type: {starter_type}
- Redundancy: {redundancy}
- Control: Cascade PID pressure control with staging/de-staging + alternation
- Communications: {twin.communication or 'Hardwired'}
- Enclosure: {enclosure}
- Cyber: IEC 62443 baseline principles

Purpose
This pack is designed as "copy/paste" material for Design Firms at Concept/FEED and Basic Design.
It provides reusable text, drawings, schedules, and templates to prescribe a complete solution approach.

Pack contents
1) 001_manifest.json
   - Package manifest and generation meta-data
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
    return content.encode('utf-8')