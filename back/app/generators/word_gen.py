import base64
import io

from docx import Document
from docx.shared import Inches
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

from ..schemas.configurator import DigitalTwinResponse
from .spec_text_gen import get_enclosure_clauses, get_starter_templates

# Source - https://stackoverflow.com/a/68530806
# Posted by JGC
# Retrieved 2026-05-29, License - CC BY-SA 4.0


# Stack overflow goated
def insertHR(paragraph):
    p = paragraph._p  # p is the <w:p> XML element
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    pPr.insert_element_before(
        pBdr,
        "w:shd",
        "w:tabs",
        "w:suppressAutoHyphens",
        "w:kinsoku",
        "w:wordWrap",
        "w:overflowPunct",
        "w:topLinePunct",
        "w:autoSpaceDE",
        "w:autoSpaceDN",
        "w:bidi",
        "w:adjustRightInd",
        "w:snapToGrid",
        "w:spacing",
        "w:ind",
        "w:contextualSpacing",
        "w:mirrorIndents",
        "w:suppressOverlap",
        "w:jc",
        "w:textDirection",
        "w:textAlignment",
        "w:textboxTightWrap",
        "w:outlineLvl",
        "w:divId",
        "w:cnfStyle",
        "w:rPr",
        "w:sectPr",
        "w:pPrChange",
    )
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "auto")
    pBdr.append(bottom)


def generate_word_from_twin(twin: DigitalTwinResponse) -> bytes:
    doc = Document()

    doc.add_heading("Application Specification Appendix", 0)
    doc.add_paragraph(f"Project Configuration DNA: {twin.config_id}")
    doc.add_paragraph(f"Water Booster Set - {twin.load_count}-pump system")

    # Add a summary of the metadata for the project if exists
    if twin.project_name:
        doc.add_paragraph(f"Project Name: {twin.project_name}")
    if twin.project_client:
        doc.add_paragraph(f"Client: {twin.project_client}")
    if twin.project_technical_manager:
        doc.add_paragraph(f"Technical Manager: {twin.project_technical_manager}")
    if twin.project_location:
        doc.add_paragraph(f"Location: {twin.project_location}")
    if twin.project_date:
        doc.add_paragraph(f"Date: {twin.project_date}")
    if twin.project_notes:
        doc.add_paragraph(f"Additional Notes: {twin.project_notes}")

    # draw a black dashed horizontal line
    insertHR(doc.add_paragraph())

    device_type = (
        twin.components[0].description if twin.components else "Variable Speed Drive"
    )
    mounting = twin.enclosure.mounting_type if twin.enclosure else "Floor Standing"
    dimensions = twin.enclosure.dimensions_mm if twin.enclosure else "N/A"
    doc.add_paragraph(
        f"{device_type} Control Panel - {twin.load_count} x {twin.motor_power_kw} kW | {dimensions} | {twin.enclosure.ip_rating} {mounting} | Cascade PID | {twin.communication}"
    )

    # 1. Purpose and How to Use
    doc.add_heading("1. Purpose and How to Use", level=1)
    doc.add_paragraph(
        "This document is a copy/paste-ready specification appendix intended for Design Firms to include in Concept/FEED and Basic Design packages. It defines a repeatable solution approach for a water booster application and enables early-stage prescription of the complete motor control solution (enclosures, protection, variable speed drives, control, communications, and testing)."
    )
    doc.add_paragraph(
        "This appendix is technology- and outcome-oriented, but references Schneider Electric solution families where applicable. Final product references (exact part numbers) shall be confirmed during detailed design by the System Integrator / Panel Builder according to local catalog, short-circuit levels, environmental conditions, and end-user standards."
    )

    # 2. Application Data Sheet
    doc.add_heading("2. Application Data Sheet", level=1)
    table = doc.add_table(rows=8, cols=2)
    table.style = "Table Grid"

    def add_row(idx, key, value):
        table.rows[idx].cells[0].text = key
        table.rows[idx].cells[1].text = value

    add_row(0, "Application", f"Water Booster Set - {twin.load_count} Pumps")
    add_row(
        1,
        "Process objective",
        "Maintain discharge pressure at setpoint across variable demand",
    )
    add_row(
        2,
        "Motor configuration",
        f"{twin.load_count} pumps x {twin.motor_power_kw} kW each",
    )
    add_row(3, "Starter type", f"{device_type} for each pump")
    add_row(
        4,
        "Control mode",
        "Cascade PID with staging/de-staging and automatic alternation",
    )
    add_row(
        5,
        "Enclosure",
        f"{twin.enclosure.ip_rating} {mounting.lower()} control panel (universal enclosure)",
    )
    add_row(
        6,
        "Communications",
        f"{twin.communication} between PLC and drives; optional uplink to SCADA",
    )

    # 3. Reference Architecture
    doc.add_heading("3. Reference Architecture", level=1)
    doc.add_paragraph(
        "The reference architecture below provides a typical power and control arrangement for a multi-pump booster set with VSD control. It is intended as an early-stage template. The detailed GA, heat dissipation, cable entry, and assembly details shall be provided by the selected panel builder."
    )

    # Inject line diagram image if base64 provided
    if hasattr(twin, "multi_line_diagram_b64") and twin.multi_line_diagram_b64:
        try:
            b64_data = twin.multi_line_diagram_b64
            if "," in b64_data:
                b64_data = b64_data.split(",")[1]
            image_data = base64.b64decode(b64_data)
            image_stream = io.BytesIO(image_data)
            doc.add_picture(image_stream, width=Inches(6.0))
            doc.add_paragraph(
                "Figure - Generated multi line diagram injected from digital twin configuration."
            )
        except Exception as e:
            doc.add_paragraph(f"[Image Generation Failed: {e}]")
    else:
        doc.add_paragraph(
            "[PLACEHOLDER: Generated multi line diagram will be inserted here when requested via UI payload.]"
        )

    # Inject reference architecture image if base64 provided
    if hasattr(twin, "reference_architecture_b64") and twin.reference_architecture_b64:
        try:
            b64_data = twin.reference_architecture_b64
            if "," in b64_data:
                b64_data = b64_data.split(",")[1]
            image_data = base64.b64decode(b64_data)
            image_stream = io.BytesIO(image_data)
            doc.add_picture(image_stream, width=Inches(6.0))
            doc.add_paragraph(
                "Figure - Generated reference architecture diagram injected from digital twin configuration."
            )
        except Exception as e:
            doc.add_paragraph(f"[Image Generation Failed: {e}]")
    else:
        doc.add_paragraph(
            "[PLACEHOLDER: Generated reference architecture diagram will be inserted here when requested via UI payload.]"
        )

    # 4. Panel Scope and Deliverables
    doc.add_heading("4. Panel Scope and Deliverables", level=1)
    doc.add_paragraph("The booster control panel assembly shall include, as a minimum:")
    doc.add_paragraph(
        "Main incoming isolator and/or MCCB sized for the panel maximum demand and fault level.",
        style="List Bullet",
    )
    doc.add_paragraph(
        f"{twin.load_count} VSD feeders sized for {twin.motor_power_kw} kW motors, including appropriate upstream protection and isolation as per applicable standards.",
        style="List Bullet",
    )
    doc.add_paragraph(
        "PLC with sufficient Ethernet capability and I/O for pressure feedback, permissives, local controls, and alarms.",
        style="List Bullet",
    )
    doc.add_paragraph(
        "Local operator interface (HMI) and basic local controls.", style="List Bullet"
    )
    doc.add_paragraph(
        f"Industrial Ethernet switch for {twin.communication} network connectivity.",
        style="List Bullet",
    )
    doc.add_paragraph(
        "Panel auxiliaries: 24 VDC power supply, control protection, terminal blocks, labeling, earthing, and service accessories (lighting/heater as required).",
        style="List Bullet",
    )
    doc.add_paragraph(
        "Documentation set: electrical drawings, I/O list, network IP plan, PLC/HMI backups, FAT/SAT records.",
        style="List Bullet",
    )

    # 5. Electrical Requirements
    doc.add_heading("5. Electrical Requirements", level=1)
    doc.add_heading("5.1 Enclosure and Assembly", level=2)
    doc.add_paragraph(
        f"The control panel enclosure shall be {mounting.lower()} with minimum ingress protection rating {twin.enclosure.ip_rating} and suitable for indoor technical room installation unless stated otherwise."
    )
    enc_lines = get_enclosure_clauses(twin)
    for line in enc_lines:
        doc.add_paragraph(line)

    doc.add_heading("5.2 Feeders", level=2)
    doc.add_paragraph(
        f"Each pump motor shall be controlled by an individual {device_type} suitable for {twin.motor_power_kw} kW motor duty and the supply network characteristics."
    )
    doc.add_paragraph(
        f"The drive shall support network control and monitoring via {twin.communication} and shall expose key operating data."
    )
    doc.add_paragraph(
        "The design shall include appropriate upstream protection and isolation for each feeder."
    )

    # dynamic feeder clauses
    device_type = twin.components[0].description if twin.components else "Motor Starter"
    comm_protocol = twin.communication if twin.communication else "Modbus TCP"

    templates = get_starter_templates(twin.series_id)
    feeder_clauses = [
        clause.format(motor_power_kw=twin.motor_power_kw)
        for clause in templates["feeders"]
    ]
    for clause in feeder_clauses:
        doc.add_paragraph(clause)

    # Append communication capabilities of the feeders
    if comm_protocol.lower() == "no":
        doc.add_paragraph(
            f"Each {device_type} shall support hardwired I/O for start/stop, speed reference, and monitoring."
        )
        doc.add_paragraph(
            f"Each {device_type} shall provide access to at least the following data via analog/digital signals: run status, fault status, and feedback."
        )
    else:
        doc.add_paragraph(
            f"Each {device_type} shall support Ethernet communications using {comm_protocol} for start/stop, speed reference, and monitoring."
        )
        doc.add_paragraph(
            f"Each {device_type} shall provide access to at least the following data: run status, feedback, current, power, energy, fault status, and fault code."
        )

    doc.add_heading("5.3 Control Power and Auxiliaries", level=2)
    doc.add_paragraph(
        "The panel shall include a 24 VDC control power supply sized for PLC, HMI, network devices, and field instrumentation loops as required."
    )
    doc.add_paragraph(
        "An emergency stop function shall remove run permission from all drives and place the system into a safe state."
    )
    doc.add_paragraph(
        "Door interlock and maintenance mode provisions shall be implemented as required by local regulations and end user standards."
    )

    # dynamic control clauses
    has_plc = str(twin.plc_included).strip().lower() in ["yes", "true", "1"]
    has_scada = str(twin.scada_included).strip().lower() in ["yes", "true", "1"]
    controller_text = (
        "a PLC" if has_plc else "a dedicated pump controller (or remote PLC)"
    )

    doc.add_paragraph(
        f"The panel shall include {controller_text} with sufficient capacity and I/O to implement required controls."
    )

    if has_scada:
        doc.add_paragraph(
            "The panel shall include a local HMI and a network uplink to a supervisory SCADA system for remote monitoring and control."
        )
    else:
        doc.add_paragraph(
            "The panel shall include a local HMI for operator control and monitoring (start/stop, setpoints, status, alarms, runtime)."
        )

    doc.add_paragraph(
        "The control system shall support a redundant discharge pressure transmitter. Upon primary signal fault/out-of-range, control shall automatically switch to the redundant transmitter and alarm.\n"
    )

    # 6. Control Philosophy
    doc.add_heading("6. Control Philosophy - Cascade PID (Booster Set)", level=1)
    controller_master_text = "The PLC" if has_plc else "The dedicated pump controller"

    if comm_protocol.lower() == "no":
        doc.add_paragraph("G. COMMUNICATIONS - HARDWIRED")
        doc.add_paragraph(
            f"Control and monitoring signals between {(controller_master_text.lower()).replace('the ', '')} and motor starters shall be hardwired via discrete and analog I/O."
        )
        doc.add_paragraph(
            "The panel shall include sufficient terminal blocks to land all interposing hardwired control links."
        )
        doc.add_paragraph(
            "Loss of critical hardwired permissives (e.g., E-Stop, pressure switch) shall transition the system to a defined safe state."
        )
    else:
        doc.add_paragraph(f"G. COMMUNICATIONS - {comm_protocol.upper()}")
        doc.add_paragraph(
            f"{controller_master_text} shall act as client/master and each motor starter shall act as a server/slave over {comm_protocol}."
        )
        doc.add_paragraph(
            "Each networked device shall have a unique IP address; an IP plan shall be provided."
        )
        doc.add_paragraph(
            "Loss of communications shall generate an alarm and the system shall transition to a defined safe state."
        )

    # 7. Communications
    doc.add_heading(f"7. Communications - {twin.communication}", level=1)
    doc.add_paragraph(
        f"The PLC shall act as master. Each drive shall be a server via {twin.communication}. The network shall be designed for deterministic control."
    )

    # 8. FAT/SAT
    doc.add_heading("8. FAT/SAT - Minimum Acceptance Tests", level=1)
    doc.add_paragraph(
        "The supplier shall provide electrical drawings (SLD, schematics, GA, terminal schedule), I/O list, network IP plan, PLC/HMI backups, and operating manuals."
    )
    doc.add_paragraph(
        "FAT shall verify wiring, labeling, communications, HMI, and core control sequences including staging/de-staging, alternation, and redundancy behavior."
    )
    doc.add_paragraph(
        "SAT shall verify field wiring, motor rotation, transmitter scaling, PID stability, and redundancy in live operation."
    )

    output = io.BytesIO()
    doc.save(output)

    output.seek(0)
    return output.read()
