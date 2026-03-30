from ...schemas.configurator import DigitalTwinResponse

def generate_readme_from_twin(twin: DigitalTwinResponse) -> bytes:
    application_type = "Water Booster Set"
    starter_type = {"DOL": "Direct-On-Line", "YD": "Star-Delta", "VFD": "Variable Speed Drive", "VSD": "Variable Speed Drive"}.get(twin.series_id, twin.series_id)
    enclosure = f"{twin.enclosure.dimensions_mm} - {twin.enclosure.mounting_type}" if twin.enclosure else "IP54 floor standing"
    redundancy = twin.bypass_strategy if twin.bypass_strategy else "[TBD-REDUNDANCY]"

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
1) EngineeringSpec_{twin.config_id}.docx
   - Copy/paste-ready specification appendix (shall language)
   - Includes reference architecture and typical multi line figure
2) Parameters.xlsx, IO-List.xlsx, Alarm_List.xlsx, BOM-Template.xlsx, Network-IP-Plan.xlsx, Option-Matrix.xlsx
   - Extracted data sheets and templates
3) MultiLineDiagram.png / .svg, ReferenceArchitecture.png / .svg
   - Generated Multi Line and Reference Architecture diagrams
4) BIM/Logical_{twin.config_id}.ifc, BIM/Visual_{twin.config_id}.ifc
   - BIM Object variants
5) DigitalTwin_DNA_{twin.config_id}.json
   - Full digital twin parameter set
6) manifest.json
   - Package manifest and generation meta-data

How to use (recommended)
- Design Firm: paste the DOCX appendix (or relevant sections) into FEED/basic design documentation.
- System Integrator/Panel Builder: confirm ratings, local standards, short-circuit levels and environment; complete BOM with exact part numbers and develop GA/wiring.

Notes
- Part numbers and selection notes are dynamically sourced from the core equipment catalog based on your load configurations.
- The solution can be extended with optional harmonic mitigation, dv/dt filters, bypass, remote SCADA integration, and additional permissives.
"""
    return content.encode('utf-8')