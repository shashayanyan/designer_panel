from typing import List
from ..schemas.configurator import DigitalTwinResponse

def get_enclosure_clauses(twin: DigitalTwinResponse) -> List[str]:
    cat_ref = twin.enclosure.catalog_ref if twin.enclosure else ""
    if "PLA" in cat_ref:
        from .templates.specs.PLA_lines import pla_lines
        return pla_lines
    elif "PLM" in cat_ref:
        from .templates.specs.PLM_lines import plm_lines
        return plm_lines
    else:
        mounting = twin.enclosure.mounting_type if twin.enclosure else "Floor Standing"
        ip_rating = "IP54"
        return [
            f"The enclosure shall be {mounting}, indoor type, minimum {ip_rating}, with provision for bottom cable entry.",
            "The panel shall include an earthing bar, internal wiring ducting, and clear labeling of devices, terminals, and cables.",
            "Thermal management shall be provided to keep internal component temperatures within manufacturer limits at maximum load and site ambient conditions."
        ]

def generate_spec_text_from_twin(twin: DigitalTwinResponse) -> bytes:
    lines = []
    
    redundancy_str = "N+1" if twin.bypass_strategy else "No redundancy"
    
    lines.append(f"WATER BOOSTER SET - {twin.load_count} PUMPS ({redundancy_str}) - CONTROL PANEL")
    lines.append("Copy/Paste Specification Clauses (v1.0)")
    lines.append("")
    
    # A. GENERAL
    lines.append("A. GENERAL")
    lines.append(f"1. The contractor shall provide a complete booster control panel assembly for a water booster set controlling {twin.load_count} pumps rated {twin.motor_power_kw} kW each.")
    lines.append(f"2. The solution shall support {redundancy_str} and cascade PID pressure control using a discharge pressure feedback signal.")
    lines.append("3. The control panel shall be designed for early-stage specification and shall be detailed by the selected system integrator/panel builder during detailed design.")
    lines.append("")
    
    # B. ENCLOSURE / MECHANICAL
    lines.append("B. ENCLOSURE / MECHANICAL")
    enc_lines = get_enclosure_clauses(twin)
    for i, line in enumerate(enc_lines, 1):
        lines.append(f"{i}. {line}")
    lines.append("")
    
    # C. POWER DISTRIBUTION AND PROTECTION
    lines.append("C. POWER DISTRIBUTION AND PROTECTION")
    lines.append("1. The panel shall include a main incoming isolator and/or MCCB sized for the maximum demand and the site fault level.")
    lines.append("2. Each feeder shall include appropriate upstream short-circuit and overload protection and a means of isolation as required by applicable standards.")
    lines.append("3. Harmonic mitigation (line reactors, filters, or equivalent) and EMC measures shall be included where required by grid code, EMC requirements, or cable length constraints.")
    lines.append("")
    
    # D. MOTOR FEEDERS
    lines.append("D. MOTOR FEEDERS")
    device_type = twin.components[0].description if twin.components else "Motor Starter"
    comm_protocol = twin.communication if twin.communication else "Modbus TCP"
    
    lines.append(f"1. Each pump motor shall be controlled by an individual {device_type} suitable for {twin.motor_power_kw} kW motor duty.")
    if comm_protocol.lower() == "no":
        lines.append(f"2. Each {device_type} shall support hardwired I/O for start/stop, speed reference, and monitoring.")
        lines.append(f"3. Each {device_type} shall provide access to at least the following data via analog/digital signals: run status, fault status, and speed/frequency feedback.")
    else:
        lines.append(f"2. Each {device_type} shall support Ethernet communications using {comm_protocol} for start/stop, speed reference, and monitoring.")
        lines.append(f"3. Each {device_type} shall provide access to at least the following data: run status, speed/frequency feedback, current, power, energy, fault status, and fault code.")
    lines.append("")
    
    # E. CONTROL SYSTEM
    has_plc = str(twin.plc_included).strip().lower() in ['yes', 'true', '1']
    has_scada = str(twin.scada_included).strip().lower() in ['yes', 'true', '1']
    controller_text = "a PLC" if has_plc else "a dedicated pump controller (or remote PLC)"
    
    lines.append("E. CONTROL SYSTEM")
    lines.append(f"1. The panel shall include {controller_text} with sufficient capacity and I/O to implement:")
    lines.append("   - Cascade PID pressure control")
    lines.append("   - Pump staging/de-staging")
    lines.append("   - Duty/standby alternation and runtime equalization")
    lines.append("   - Redundancy and fault handling")
    
    if has_scada:
        lines.append("2. The panel shall include a local HMI and a network uplink to a supervisory SCADA system for remote monitoring and control.")
    else:
        lines.append("2. The panel shall include a local HMI for operator control and monitoring (start/stop, setpoints, status, alarms, runtime).")
        
    lines.append("3. The control system shall support a redundant discharge pressure transmitter. Upon primary signal fault/out-of-range, control shall automatically switch to the redundant transmitter and alarm.")
    lines.append("")
    
    # F. CONTROL PHILOSOPHY
    lines.append("F. CONTROL PHILOSOPHY - MINIMUM FUNCTIONAL REQUIREMENTS")
    lines.append("1. Demand detection: start lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.")
    lines.append("2. Staging logic: add pumps when the system cannot maintain setpoint (e.g., lead speed above a configurable threshold for a configurable time).")
    lines.append("3. De-staging logic: remove pumps when demand decreases (e.g., average speed below a configurable threshold for a configurable time) while maintaining stable pressure.")
    lines.append("4. Anti-short-cycle: minimum run time and minimum stop time shall be implemented for each pump.")
    lines.append("5. Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear.")
    lines.append("6. Failure handling: if any pump/drive becomes unavailable, remaining pumps shall continue to control pressure within available capacity and generate an alarm.")
    lines.append("")
    
    # G. COMMUNICATIONS
    controller_master_text = "The PLC" if has_plc else "The dedicated pump controller"
    
    if comm_protocol.lower() == "no":
        lines.append("G. COMMUNICATIONS - HARDWIRED")
        lines.append(f"1. Control and monitoring signals between {(controller_master_text.lower()).replace('the ', '')} and motor starters shall be hardwired via discrete and analog I/O.")
        lines.append("2. The panel shall include sufficient terminal blocks to land all interposing hardwired control links.")
        lines.append("3. Loss of critical hardwired permissives (e.g., E-Stop, pressure switch) shall transition the system to a defined safe state.")
    else:
        lines.append(f"G. COMMUNICATIONS - {comm_protocol.upper()}")
        lines.append(f"1. {controller_master_text} shall act as client/master and each motor starter shall act as a server/slave over {comm_protocol}.")
        lines.append("2. Each networked device shall have a unique IP address; an IP plan shall be provided.")
        lines.append("3. Loss of communications shall generate an alarm and the system shall transition to a defined safe state.")
    lines.append("")
    
    # H. CYBERSECURITY
    lines.append("H. CYBERSECURITY BASELINE (IEC 62443-ALIGNED)")
    lines.append("1. The control network shall be treated as an industrial control zone and shall be logically separated from corporate networks.")
    lines.append("2. Default passwords shall be changed; role-based access and unique user accounts shall be applied where supported.")
    lines.append("3. Remote access (if required) shall use secure methods with MFA and audit trail; direct internet access to the control network shall not be permitted.")
    lines.append("4. Security-relevant events (login attempts, configuration changes, comms loss) shall be logged.")
    lines.append("")
    
    # I. DOCUMENTATION AND TESTING
    lines.append("I. DOCUMENTATION AND TESTING")
    lines.append("1. The supplier shall provide electrical drawings (SLD, schematics, GA, terminal schedule), I/O list, network IP plan, PLC/HMI backups, and operating manuals.")
    lines.append("2. FAT shall verify wiring, labeling, communications, HMI, and core control sequences including staging/de-staging, alternation, and redundancy behavior.")
    lines.append("3. SAT shall verify field wiring, motor rotation, transmitter scaling, PID stability, and redundancy in live operation.")

    content = "\n".join(lines)
    return content.encode('utf-8')
