import io
import base64
from docx import Document
from docx.shared import Inches
from ..schemas.configurator import DigitalTwinResponse

def generate_word_from_twin(twin: DigitalTwinResponse) -> bytes:
    doc = Document()
    
    doc.add_heading(f"Application Specification Appendix", 0)
    doc.add_paragraph(f"Project Configuration DNA: {twin.config_id}")
    doc.add_paragraph(f"Water Booster Set - {twin.load_count}-pump system")
    
    device_type = twin.components[0].description if twin.components else "Variable Speed Drive"
    mounting = twin.enclosure.mounting_type if twin.enclosure else "Floor Standing"
    dimensions = twin.enclosure.dimensions_mm if twin.enclosure else "N/A"
    doc.add_paragraph(f"{device_type} Control Panel - {twin.load_count} x {twin.motor_power_kw} kW | {dimensions} | IP54 {mounting} | Cascade PID | {twin.communication} | IEC 62443 Baseline")
    
    # 1. Purpose and How to Use
    doc.add_heading("1. Purpose and How to Use", level=1)
    doc.add_paragraph("This document is a copy/paste-ready specification appendix intended for Design Firms to include in Concept/FEED and Basic Design packages. It defines a repeatable solution approach for a water booster application and enables early-stage prescription of the complete motor control solution (enclosures, protection, variable speed drives, control, communications, and testing).")
    doc.add_paragraph("This appendix is technology- and outcome-oriented, but references Schneider Electric solution families where applicable. Final product references (exact part numbers) shall be confirmed during detailed design by the System Integrator / Panel Builder according to local catalog, short-circuit levels, environmental conditions, and end-user standards.")

    # 2. Application Data Sheet
    doc.add_heading("2. Application Data Sheet", level=1)
    table = doc.add_table(rows=8, cols=2)
    table.style = 'Table Grid'
    
    def add_row(idx, key, value):
        table.rows[idx].cells[0].text = key
        table.rows[idx].cells[1].text = value

    add_row(0, "Application", f"Water Booster Set - {twin.load_count} Pumps")
    add_row(1, "Process objective", "Maintain discharge pressure at setpoint across variable demand")
    add_row(2, "Motor configuration", f"{twin.load_count} pumps x {twin.motor_power_kw} kW each")
    add_row(3, "Starter type", f"{device_type} for each pump")
    add_row(4, "Control mode", "Cascade PID with staging/de-staging and automatic alternation")
    add_row(5, "Enclosure", f"IP54 {mounting.lower()} control panel (universal enclosure)")
    add_row(6, "Communications", f"{twin.communication} between PLC and drives; optional uplink to SCADA")
    add_row(7, "Cybersecurity", "Baseline requirements aligned with IEC 62443 principles (zones, accounts, logging)")

    # 3. Reference Architecture
    doc.add_heading("3. Reference Architecture", level=1)
    doc.add_paragraph("The reference architecture below provides a typical power and control arrangement for a multi-pump booster set with VSD control. It is intended as an early-stage template. The detailed GA, heat dissipation, cable entry, and assembly details shall be provided by the selected panel builder.")
    
    # Inject line diagram image if base64 provided
    if hasattr(twin, 'multi_line_diagram_b64') and twin.multi_line_diagram_b64:
        try:
            b64_data = twin.multi_line_diagram_b64
            if "," in b64_data:
                b64_data = b64_data.split(",")[1]
            image_data = base64.b64decode(b64_data)
            image_stream = io.BytesIO(image_data)
            doc.add_picture(image_stream, width=Inches(6.0))
            doc.add_paragraph("Figure - Generated multi line diagram injected from digital twin configuration.")
        except Exception as e:
            doc.add_paragraph(f"[Image Generation Failed: {e}]")
    else:
        doc.add_paragraph("[PLACEHOLDER: Generated multi line diagram will be inserted here when requested via UI payload.]")

    # 4. Panel Scope and Deliverables
    doc.add_heading("4. Panel Scope and Deliverables", level=1)
    doc.add_paragraph("The booster control panel assembly shall include, as a minimum:")
    doc.add_paragraph("Main incoming isolator and/or MCCB sized for the panel maximum demand and fault level.", style='List Bullet')
    doc.add_paragraph(f"{twin.load_count} VSD feeders sized for {twin.motor_power_kw} kW motors, including appropriate upstream protection and isolation as per applicable standards.", style='List Bullet')
    doc.add_paragraph(f"PLC with sufficient Ethernet capability and I/O for pressure feedback, permissives, local controls, and alarms.", style='List Bullet')
    doc.add_paragraph("Local operator interface (HMI) and basic local controls.", style='List Bullet')
    doc.add_paragraph(f"Industrial Ethernet switch for {twin.communication} network connectivity.", style='List Bullet')
    doc.add_paragraph("Panel auxiliaries: 24 VDC power supply, control protection, terminal blocks, labeling, earthing, and service accessories (lighting/heater as required).", style='List Bullet')
    doc.add_paragraph("Documentation set: electrical drawings, I/O list, network IP plan, PLC/HMI backups, FAT/SAT records.", style='List Bullet')

    # 5. Electrical Requirements
    doc.add_heading("5. Electrical Requirements", level=1)
    doc.add_heading("5.1 Enclosure and Assembly", level=2)
    doc.add_paragraph(f"The control panel enclosure shall be {mounting.lower()} with minimum ingress protection rating IP54 and suitable for indoor technical room installation unless stated otherwise.")
    doc.add_paragraph("The enclosure shall include a gland plate (or equivalent) for bottom cable entry, earthing bar, and provision for safe maintenance access.")
    doc.add_paragraph("The panel builder shall provide thermal management (fan/filter or air conditioning as required) to maintain component temperatures within manufacturer limits at site ambient conditions.")
    doc.add_paragraph("All components shall be clearly labeled; wiring shall be ferruled and identified in accordance with the drawings.")
    doc.add_paragraph("The assembly shall be designed, manufactured, and tested in accordance with applicable IEC requirements for low-voltage switchgear and controlgear assemblies (e.g., IEC 61439 where applicable).")

    doc.add_heading("5.2 Feeders", level=2)
    doc.add_paragraph(f"Each pump motor shall be controlled by an individual {device_type} suitable for {twin.motor_power_kw} kW motor duty and the supply network characteristics.")
    doc.add_paragraph(f"The drive shall support network control and monitoring via {twin.communication} and shall expose key operating data.")
    doc.add_paragraph("The design shall include appropriate upstream protection and isolation for each feeder.")

    doc.add_heading("5.3 Control Power and Auxiliaries", level=2)
    doc.add_paragraph("The panel shall include a 24 VDC control power supply sized for PLC, HMI, network devices, and field instrumentation loops as required.")
    doc.add_paragraph("An emergency stop function shall remove run permission from all drives and place the system into a safe state.")
    doc.add_paragraph("Door interlock and maintenance mode provisions shall be implemented as required by local regulations and end user standards.")

    # 6. Control Philosophy
    doc.add_heading("6. Control Philosophy - Cascade PID (Booster Set)", level=1)
    doc.add_paragraph(f"The booster set shall maintain discharge pressure at a configurable setpoint using cascade PID control and automatic staging of {twin.load_count} pumps. The PLC shall coordinate drive start/stop and speed references over {twin.communication}.")
    doc.add_paragraph("Minimum functional requirements:\n"
                      "- PID pressure control using a primary discharge pressure transmitter.\n"
                      "- Pump staging/de-staging based on demand thresholds.\n"
                      "- Automatic alternation of duty to equalize runtime.\n"
                      "- Failover: if any pump/drive becomes unavailable, remaining pumps shall continue to control pressure.")

    # 7. Communications
    doc.add_heading(f"7. Communications - {twin.communication}", level=1)
    doc.add_paragraph(f"The PLC shall act as master. Each drive shall be a server via {twin.communication}. The network shall be designed for deterministic control.")

    # 8. Cybersecurity
    doc.add_heading("8. Cybersecurity Baseline (IEC 62443-aligned)", level=1)
    doc.add_paragraph("This project shall implement baseline cybersecurity controls consistent with IEC 62443 principles.")

    # 9. FAT/SAT
    doc.add_heading("9. FAT/SAT - Minimum Acceptance Tests", level=1)
    doc.add_paragraph("Factory Acceptance Test (FAT) & Site Acceptance Test (SAT) shall include visual, electrical, network, functional, and HMI validations per standard clauses.")

    output = io.BytesIO()
    doc.save(output)
    
    output.seek(0)
    return output.read()
