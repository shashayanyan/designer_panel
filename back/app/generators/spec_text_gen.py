from typing import List, Dict
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


def get_starter_templates(series_id: str) -> Dict[str, List[str]]:
    """Fetches the appropriate clause templates based on the motor starter type."""
    series = series_id.upper() if series_id else "DOL"

    # Map the incoming series_id to the appropriate dictionaries
    if "ATS01" in series:
        from .templates.specs.ats01_clauses import ats01_motor_feeders, ats01_control_philosophy
        return {"feeders": ats01_motor_feeders, "philosophy": ats01_control_philosophy}
    elif "ATS130" in series:
        from .templates.specs.ats130_clauses import ats130_motor_feeders, ats130_control_philosophy
        return {"feeders": ats130_motor_feeders, "philosophy": ats130_control_philosophy}
    elif "VSD" in series or "ATV" in series:
        from .templates.specs.vsd_clauses import vsd_motor_feeders, vsd_control_philosophy
        return {"feeders": vsd_motor_feeders, "philosophy": vsd_control_philosophy}
    else:
        from .templates.specs.dol_clauses import dol_motor_feeders, dol_control_philosophy
        return {"feeders": dol_motor_feeders, "philosophy": dol_control_philosophy}

def generate_spec_text_from_twin(twin: DigitalTwinResponse) -> bytes:
    lines = []
    
    redundancy_str = "N+1" if twin.bypass_strategy else "No redundancy"
    
    lines.append(f"WATER BOOSTER SET - {twin.load_count} PUMPS ({redundancy_str}) - {twin.config_id}")
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
    
    templates = get_starter_templates(twin.series_id)
    feeder_clauses = [clause.format(motor_power_kw=twin.motor_power_kw) for clause in templates["feeders"]]
    for i, clause in enumerate(feeder_clauses, 1):
        lines.append(f"{i}. {clause}")
    
    # Append communication capabilities of the feeders
    next_idx = len(feeder_clauses) + 1
    if comm_protocol.lower() == "no":
        lines.append(f"{next_idx}. Each {device_type} shall support hardwired I/O for start/stop, speed reference, and monitoring.")
        lines.append(f"{next_idx + 1}. Each {device_type} shall provide access to at least the following data via analog/digital signals: run status, fault status, and feedback.")
    else:
        lines.append(f"{next_idx}. Each {device_type} shall support Ethernet communications using {comm_protocol} for start/stop, speed reference, and monitoring.")
        lines.append(f"{next_idx + 1}. Each {device_type} shall provide access to at least the following data: run status, feedback, current, power, energy, fault status, and fault code.")
    lines.append("")
    
    # E. CONTROL SYSTEM
    has_plc = str(twin.plc_included).strip().lower() in ['yes', 'true', '1']
    has_scada = str(twin.scada_included).strip().lower() in ['yes', 'true', '1']
    controller_text = "a PLC" if has_plc else "a dedicated pump controller (or remote PLC)"
    
    lines.append("E. CONTROL SYSTEM")
    lines.append(f"1. The panel shall include {controller_text} with sufficient capacity and I/O to implement required controls.")
    
    if has_scada:
        lines.append("2. The panel shall include a local HMI and a network uplink to a supervisory SCADA system for remote monitoring and control.")
    else:
        lines.append("2. The panel shall include a local HMI for operator control and monitoring (start/stop, setpoints, status, alarms, runtime).")
        
    lines.append("3. The control system shall support a redundant discharge pressure transmitter. Upon primary signal fault/out-of-range, control shall automatically switch to the redundant transmitter and alarm.\n")
    
    # F. CONTROL PHILOSOPHY
    lines.append("F. CONTROL PHILOSOPHY - MINIMUM FUNCTIONAL REQUIREMENTS")
    for i, clause in enumerate(templates["philosophy"], 1):
         lines.append(f"{i}. {clause}")
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
