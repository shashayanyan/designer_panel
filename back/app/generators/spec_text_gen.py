from typing import Dict, List

from ..schemas.configurator import DigitalTwinResponse


def is_yes(value) -> bool:
    return str(value or "").strip().lower() in ["yes", "true", "1"]


def is_real_selection(value) -> bool:
    return str(value or "").strip().lower() not in [
        "",
        "no",
        "none",
        "n/a",
        "na",
        "null",
    ]


def get_comm_mode(twin) -> str:
    comm = str(getattr(twin, "communication", "") or "").strip().lower()

    if comm in ["", "no", "none", "hardwired"]:
        return "hardwired"

    if "modbus" in comm:
        return "modbus"

    if "profinet" in comm or "profi" in comm:
        return "profinet"

    return comm


def get_comm_label(twin) -> str:
    mode = get_comm_mode(twin)
    raw = str(getattr(twin, "communication", "") or "").strip()

    if mode == "hardwired":
        return "Hardwired"

    if mode == "modbus":
        return raw or "Modbus"

    if mode == "profinet":
        return raw or "ProfiNet"

    return raw or mode


def get_component_text(twin) -> str:
    components = getattr(twin, "components", []) or []
    return " ".join(
        [
            f"{getattr(c, 'part_number', '') or ''} "
            f"{getattr(c, 'description', '') or ''} "
            f"{getattr(c, 'item_category', '') or ''}"
            for c in components
        ]
    ).upper()


def get_starter_kind(twin) -> str:
    series_id = str(getattr(twin, "series_id", "") or "").strip().upper()
    series_name = str(getattr(twin, "series_name", "") or "").strip().upper()
    component_text = get_component_text(twin)

    text = f"{series_id} {series_name} {component_text}"
    if (
        series_id in ["DOL_ADV", "DOLADV", "DOL_ADVANCED"]
        or "DIRECT ON LINE ADVANCED" in text
        or "DIRECT-ON-LINE ADVANCED" in text
        or ("DOL" in text and "ADVANCED" in text)
    ):
        return "dol_adv"

    if series_id == "DOL" or "DIRECT ON LINE" in text or "DIRECT-ON-LINE" in text:
        return "dol"

    if "ATS01" in text:
        return "ats01"

    if series_id == "SS" or "SOFT STARTER" in text or "ATS130" in text:
        return "ats130"

    if (
        series_id in ["VSD", "VFD"]
        or "VARIABLE SPEED" in text
        or "VARIABLE SPEED DRIVE" in text
        or "ATV" in text
    ):
        return "vfd"

    return "motor_starter"


def get_starter_display_name(twin) -> str:
    kind = get_starter_kind(twin)

    if kind == "dol_adv":
        return "Direct-on-Line Starter with Advanced Motor Management"

    if kind == "dol":
        return "Direct-on-Line Starter"

    if kind in ["ats01", "ats130"]:
        return "Soft Starter"

    if kind == "vfd":
        return "Variable Speed Drive (VSD)"

    return "Motor Starter"


def supports_speed_reference(twin) -> bool:
    return get_starter_kind(twin) == "vfd"


def build_spec_context(twin):
    comm_mode = get_comm_mode(twin)

    return {
        "has_plc": is_yes(getattr(twin, "plc_included", "No")),
        "has_scada": is_yes(getattr(twin, "scada_included", "No")),
        "comm_mode": comm_mode,
        "comm_label": get_comm_label(twin),
        "has_network": comm_mode in ["modbus", "profinet"],
        "starter_kind": get_starter_kind(twin),
        "device_type": get_starter_display_name(twin),
        "supports_speed_reference": supports_speed_reference(twin),
    }


def get_communication_subject(ctx) -> str:
    starter_kind = ctx["starter_kind"]
    device_type = ctx["device_type"]

    if starter_kind in ["dol", "dol_adv"]:
        return "The booster panel control/interface devices"

    if starter_kind in ["ats01", "ats130"]:
        return f"Each {device_type} or associated communication accessory"

    if starter_kind == "vfd":
        return f"Each {device_type}"

    return "The selected motor starter/control interface"


def get_enclosure_clauses(twin: DigitalTwinResponse) -> List[str]:
    cat_ref = twin.enclosure.catalog_ref if twin.enclosure else ""

    if "PLA" in cat_ref:
        from .templates.specs.PLA_lines import pla_lines

        return pla_lines

    elif "PLM" in cat_ref:
        from .templates.specs.PLM_lines import plm_lines

        return plm_lines

    elif "CRN" in cat_ref:
        from .templates.specs.CRN_lines import crn_lines

        return crn_lines

    elif "S3D" in cat_ref:
        from .templates.specs.S3D_lines import s3d_lines

        return s3d_lines

    elif "SFN" in cat_ref:
        from .templates.specs.SFN_lines import sfn_lines

        return sfn_lines

    elif "SM" in cat_ref:
        from .templates.specs.SM_lines import sm_lines

        return sm_lines

    else:
        mounting = twin.enclosure.mounting_type if twin.enclosure else "Floor Standing"
        ip_rating = twin.enclosure.ip_rating if twin.enclosure else "IP54"

        return [
            f"The enclosure shall be {mounting}, indoor type, minimum {ip_rating}, with provision for bottom cable entry.",
            "The panel shall include an earthing bar, internal wiring ducting, and clear labeling of devices, terminals, and cables.",
            "Thermal management shall be provided to keep internal component temperatures within manufacturer limits at maximum load and site ambient conditions.",
        ]


def get_starter_templates(twin: DigitalTwinResponse) -> Dict[str, List[str]]:
    """Fetches the appropriate clause templates based on the motor starter type."""
    starter_kind = get_starter_kind(twin)

    if starter_kind == "ats01":
        from .templates.specs.ats01_clauses import (
            ats01_control_philosophy,
            ats01_motor_feeders,
        )

        return {
            "feeders": ats01_motor_feeders,
            "philosophy": ats01_control_philosophy,
        }

    if starter_kind == "ats130":
        from .templates.specs.ats130_clauses import (
            ats130_control_philosophy,
            ats130_motor_feeders,
        )

        return {
            "feeders": ats130_motor_feeders,
            "philosophy": ats130_control_philosophy,
        }

    if starter_kind == "vfd":
        from .templates.specs.vsd_clauses import (
            vsd_control_philosophy,
            vsd_motor_feeders,
        )

        return {
            "feeders": vsd_motor_feeders,
            "philosophy": vsd_control_philosophy,
        }

    if starter_kind == "dol_adv":
        from .templates.specs.dola_clauses import (
            dol_advanced_control_philosophy,
            dol_advanced_motor_feeders,
        )

        return {
            "feeders": dol_advanced_motor_feeders,
            "philosophy": dol_advanced_control_philosophy,
        }

    from .templates.specs.dol_clauses import (
        dol_control_philosophy,
        dol_motor_feeders,
    )

    return {
        "feeders": dol_motor_feeders,
        "philosophy": dol_control_philosophy,
    }


def get_safe_control_philosophy_clauses(
    ctx, templates: Dict[str, List[str]]
) -> List[str]:
    """
    Avoids claiming that the panel implements automatic sequencing when PLC is not included.
    If PLC is included, the starter-specific templates can be used directly.
    If PLC is not included, the panel supports external sequencing/control.
    """
    starter_kind = ctx["starter_kind"]
    has_plc = ctx["has_plc"]

    if has_plc:
        return templates["philosophy"]

    if starter_kind == "vfd":
        return [
            "Demand detection and PID pressure control shall be implemented by the external controller, site control system, or VSD-native functions where configured.",
            "The panel shall provide the required interfaces for pump start/stop, speed reference where applicable, run feedback, fault feedback, and permissives.",
            "Pump staging, de-staging, and alternation shall be implemented by the external controller or site control system where required.",
            "Failure handling shall be implemented through available status, fault, and permissive signals from the selected devices.",
        ]

    if starter_kind in ["ats01", "ats130"]:
        return [
            "Demand detection and pressure-based staging shall be implemented by the external controller or site control system where required.",
            "The panel shall provide the required interfaces for soft starter start/stop control, run feedback, fault feedback, reset where applicable, and permissives.",
            "Pump staging, de-staging, and alternation shall be implemented by the external controller or site control system where required.",
            "Failure handling shall be implemented through available status, fault, and permissive signals from the selected devices.",
        ]

    if starter_kind == "dol_adv":
        return [
            "Demand detection and pressure-based staging shall be implemented by the external controller or site control system where required.",
            "The panel shall provide the required interfaces for DOL starter start/stop control, run feedback, fault feedback, motor-management trip indication, reset where applicable, diagnostics, and permissives.",
            "Pump staging, de-staging, anti-short-cycle timing, and alternation shall be implemented by the external controller or site control system where required.",
            "Failure handling shall be implemented through available status, fault, diagnostic, and permissive signals from the selected DOL starter assemblies with advanced motor management.",
        ]

    if starter_kind == "dol":
        return [
            "Demand detection and pressure-based staging shall be implemented by the external controller or site control system where required.",
            "The panel shall provide the required interfaces for DOL starter start/stop control, run feedback, fault feedback, overload trip indication, reset where applicable, and permissives.",
            "Pump staging, de-staging, anti-short-cycle timing, and alternation shall be implemented by the external controller or site control system where required.",
            "Failure handling shall be implemented through available status, fault, and permissive signals from the selected DOL starter assemblies.",
        ]

    return [
        "The panel shall provide the required control and monitoring interfaces for the selected motor starter technology.",
        "Pump sequencing, alternation, and failure handling shall be implemented by the selected controller or site control system where required.",
    ]


def generate_spec_text_from_twin(twin: DigitalTwinResponse) -> bytes:
    lines = []

    ctx = build_spec_context(twin)
    has_plc = ctx["has_plc"]
    has_scada = ctx["has_scada"]
    has_network = ctx["has_network"]
    comm_mode = ctx["comm_mode"]
    comm_label = ctx["comm_label"]
    starter_kind = ctx["starter_kind"]
    device_type = ctx["device_type"]

    templates = get_starter_templates(twin)

    lines.append(
        f"WATER BOOSTER SET - {twin.load_count} PUMPS ({device_type}) - {twin.config_id}"
    )
    lines.append("Copy/Paste Specification Clauses (v1.0)")
    lines.append("")

    # A. GENERAL
    lines.append("A. GENERAL")
    lines.append(
        f"1. The contractor shall provide a complete booster control panel assembly for a water booster set controlling {twin.load_count} pumps rated {twin.motor_power_kw} kW each."
    )

    if starter_kind == "vfd":
        lines.append(
            "2. The solution shall support pressure control using discharge pressure feedback, pump staging/de-staging, and automatic alternation where provided by the selected controller."
        )
    else:
        lines.append(
            "2. The solution shall support pressure-based pump staging/de-staging using start/stop control and automatic alternation where provided by the selected controller."
        )

    lines.append(
        "3. The control panel shall be designed for early-stage specification and shall be detailed by the selected system integrator/panel builder during detailed design."
    )
    lines.append("")

    # B. ENCLOSURE / MECHANICAL
    lines.append("B. ENCLOSURE / MECHANICAL")
    enc_lines = get_enclosure_clauses(twin)
    for i, line in enumerate(enc_lines, 1):
        lines.append(f"{i}. {line}")
    lines.append("")

    # C. POWER DISTRIBUTION AND PROTECTION
    lines.append("C. POWER DISTRIBUTION AND PROTECTION")
    lines.append(
        "1. The panel shall include a main incoming isolator and/or MCCB sized for the maximum demand and the site fault level."
    )
    lines.append(
        "2. Each feeder shall include appropriate upstream short-circuit and overload protection and a means of isolation as required by applicable standards."
    )

    if starter_kind == "vfd":
        lines.append(
            "3. Harmonic mitigation, EMC filters, line reactors, or equivalent measures shall be included where required by grid code, EMC requirements, or cable length constraints."
        )
    elif starter_kind in ["ats01", "ats130"]:
        lines.append(
            "3. Coordination, short-circuit protection, thermal protection, and starting duty shall be verified for the selected soft starter and motor characteristics."
        )
    elif starter_kind == "dol_adv":
        lines.append(
            "3. Coordination, short-circuit protection, electronic motor protection, communication interfaces where applicable, and utilization category shall be verified for the selected DOL starter assembly with advanced motor management and motor characteristics."
        )
    elif starter_kind == "dol":
        lines.append(
            "3. Coordination, short-circuit protection, overload protection, and utilization category shall be verified for the selected DOL starter assembly and motor characteristics."
        )
    else:
        lines.append(
            "3. Protection, coordination, and installation requirements shall be verified for the selected motor starter technology and motor characteristics."
        )
    lines.append("")

    # D. MOTOR FEEDERS
    lines.append("D. MOTOR FEEDERS")
    feeder_clauses = [
        clause.format(motor_power_kw=twin.motor_power_kw)
        for clause in templates["feeders"]
    ]

    for i, clause in enumerate(feeder_clauses, 1):
        lines.append(f"{i}. {clause}")

    next_idx = len(feeder_clauses) + 1

    if comm_mode == "hardwired":
        if starter_kind == "vfd":
            lines.append(
                f"{next_idx}. Each {device_type} shall support hardwired I/O for start/stop, speed reference, run feedback, fault feedback, and monitoring."
            )
        elif starter_kind == "dol_adv":
            lines.append(
                f"{next_idx}. Each DOL starter with advanced motor management shall provide hardwired interfaces for start command, stop command or run permissive, run feedback, fault feedback, motor-management trip indication, reset where applicable, diagnostics, and monitoring."
            )
        elif starter_kind == "dol":
            lines.append(
                f"{next_idx}. Each DOL starter shall provide hardwired interfaces for start command, stop command or run permissive, run feedback, fault feedback, overload trip indication, reset where applicable, and monitoring."
            )
        else:
            lines.append(
                f"{next_idx}. Each {device_type} shall support hardwired I/O for start command, stop command or run permissive, run feedback, fault feedback, reset where applicable, and monitoring."
            )
    else:
        comm_subject = get_communication_subject(ctx)

        if starter_kind == "vfd":
            lines.append(
                f"{next_idx}. {comm_subject} shall support {comm_label} communications for start/stop, speed reference, status, diagnostics, and monitoring."
            )
        elif starter_kind == "dol_adv":
            lines.append(
                f"{next_idx}. {comm_subject} shall provide {comm_label}-capable interfaces for pump start/stop commands, run feedback, ready status, fault status, motor-management diagnostics, reset where applicable, and monitoring, where included in the selected architecture."
            )
        elif starter_kind == "dol":
            lines.append(
                f"{next_idx}. {comm_subject} shall provide {comm_label}-capable interfaces for pump start/stop commands, run feedback, ready status, fault status, reset where applicable, and diagnostics, where included in the selected architecture."
            )
        else:
            lines.append(
                f"{next_idx}. {comm_subject} shall support {comm_label} communications for command, status, diagnostics, and monitoring where supported by the selected device."
            )

    lines.append("")

    # E. CONTROL SYSTEM
    lines.append("E. CONTROL SYSTEM")

    if has_plc:
        lines.append(
            "1. The panel shall include a PLC with sufficient capacity and I/O to implement the required booster control functions."
        )
    else:
        if comm_mode == "hardwired":
            lines.append(
                "1. Where no PLC is included in the panel, the panel shall provide the required hardwired interfaces for connection to an external pump controller, BMS, or site control system."
            )
        else:
            lines.append(
                "1. Where no PLC is included in the panel, the panel shall provide the required hardwired and/or communication interfaces for connection to an external pump controller, BMS, or site control system."
            )

    if has_scada:
        if has_plc:
            lines.append(
                "2. Operator control and monitoring shall be provided through local hardwired devices and PLC I/O as defined by the selected control architecture."
            )
        else:
            lines.append(
                "2. SCADA integration shall be provided through the external controller, BMS, or site control system connected to the panel interfaces."
            )
    else:
        if has_plc:
            lines.append(
                "2. Operator control and monitoring shall be provided through local hardwired devices and PLC I/O as defined by the selected control architecture."
            )
        else:
            lines.append(
                "2. Operator control and monitoring shall be provided through local hardwired devices and/or by the external controller as defined by the selected architecture."
            )

    lines.append(
        "3. Pressure transmitter quantity, redundancy, scaling, and failover behavior shall be implemented according to the selected I/O configuration and project requirements."
    )
    lines.append("")

    # F. CONTROL PHILOSOPHY
    lines.append("F. CONTROL PHILOSOPHY - MINIMUM FUNCTIONAL REQUIREMENTS")
    philosophy_clauses = get_safe_control_philosophy_clauses(ctx, templates)
    for i, clause in enumerate(philosophy_clauses, 1):
        lines.append(f"{i}. {clause}")
    lines.append("")

    # G. COMMUNICATIONS

    if has_plc:
        loss_comm_clause = (
            "Loss of communications shall generate an alarm and the PLC shall transition "
            "the booster set to a defined safe state according to the control philosophy."
        )
    else:
        loss_comm_clause = (
            "Loss of communications shall generate an alarm where communication monitoring "
            "is implemented, and the required fail-safe response shall be defined in the "
            "external controller or site control system according to the control philosophy."
        )

    if comm_mode == "hardwired":
        lines.append("G. COMMUNICATIONS - HARDWIRED")
        controller_text = (
            "PLC" if has_plc else "external controller or site control system"
        )
        lines.append(
            f"1. Control and monitoring signals between the {controller_text} and the booster panel shall be hardwired via discrete and analog I/O."
        )
        lines.append(
            "2. The panel shall include sufficient terminal blocks for pump commands, run feedback, fault feedback, reset signals, permissives, pressure signals, and alarm interfaces as required."
        )
        lines.append(
            "3. Loss of critical hardwired permissives, such as emergency stop or pressure protection signals, shall transition the booster set to a defined safe state."
        )

    elif comm_mode == "modbus":
        lines.append(f"G. COMMUNICATIONS - {comm_label.upper()}")

        if has_plc:
            lines.append(
                f"1. The PLC shall exchange command, status, and diagnostic data with the selected communication-capable devices over {comm_label}."
            )
        else:
            lines.append(
                f"1. The panel shall provide {comm_label}-capable interface points or devices for connection to the external controller, BMS, or site control system, where included in the selected architecture."
            )

        lines.append(
            "2. The Modbus address map, communication parameters, timeout behavior, and available data points shall be documented."
        )

    elif comm_mode == "profinet":
        lines.append(f"G. COMMUNICATIONS - {comm_label.upper()}")

        if has_plc:
            lines.append(
                f"1. The PLC shall exchange cyclic command, status, and diagnostic data with the selected communication-capable devices over {comm_label}."
            )
        else:
            lines.append(
                f"1. The panel shall provide {comm_label}-capable interface points or devices for connection to the external controller, BMS, or site control system, where included in the selected architecture."
            )

        lines.append(
            "2. ProfiNet device names, IP addresses where applicable, GSDML files, diagnostic data, and network topology shall be documented where applicable."
        )

    else:
        lines.append(f"G. COMMUNICATIONS - {comm_label.upper()}")
        lines.append(
            f"1. The selected communication interface shall support command, status, diagnostics, and monitoring over {comm_label} where included in the selected architecture."
        )
        lines.append(
            "2. Addressing, communication parameters, available data points, and timeout behavior shall be documented where applicable."
        )

    if comm_mode != "hardwired":
        lines.append(f"3. {loss_comm_clause}")

    lines.append("")

    # H. CYBERSECURITY
    lines.append("H. CYBERSECURITY BASELINE")

    if has_network or has_scada or has_plc:
        lines.append(
            "1. Networked control equipment shall be treated as part of an industrial control zone and shall be logically separated from corporate networks where applicable."
        )
        lines.append(
            "2. Default passwords shall be changed; role-based access and unique user accounts shall be applied where supported."
        )
        lines.append(
            "3. Remote access, if required, shall use secure methods with MFA and audit trail where supported; direct internet access to the control network shall not be permitted."
        )
        lines.append(
            "4. Security-relevant events, such as login attempts, configuration changes, and communication loss, shall be logged where supported."
        )
    else:
        lines.append(
            "1. Where no networked control equipment is included in the panel, cybersecurity requirements shall apply to any external controller, supervisory system, or site network connected by others."
        )

    lines.append("")

    # I. DOCUMENTATION AND TESTING
    lines.append("I. DOCUMENTATION AND TESTING")

    deliverables = [
        "electrical drawings",
        "single-line diagram",
        "control schematics",
        "general arrangement drawing",
        "terminal schedule",
        "BOM",
        "operating and maintenance manuals",
        "FAT/SAT records",
    ]

    if has_plc:
        deliverables.extend(["I/O list", "PLC program backup"])

    if comm_mode == "hardwired":
        deliverables.append("hardwired interface schedule")
    else:
        deliverables.extend(
            [
                "network architecture",
                "addressing plan where applicable",
                "communication parameter list",
                "available data point list",
            ]
        )

    if has_scada:
        deliverables.append("SCADA interface description")

    lines.append("1. The supplier shall provide: " + ", ".join(deliverables) + ".")

    fat_items = [
        "wiring",
        "labeling",
        "protection device settings",
        (
            "DOL starter operation"
            if starter_kind in ["dol", "dol_adv"]
            else f"{device_type} operation"
        ),
        "local controls",
        "fault indication",
    ]

    if has_plc:
        fat_items.append("automatic booster control sequences")

    if starter_kind == "dol_adv":
        fat_items.append(
            "advanced motor-management protection and diagnostic functions"
        )

    if comm_mode != "hardwired":
        fat_items.append(f"{comm_label} communication/interface tests")

    if starter_kind == "vfd":
        fat_items.append("speed reference and pressure control response")

    lines.append("2. FAT shall verify " + ", ".join(fat_items) + ".")

    sat_items = [
        "field wiring",
        "motor rotation",
        (
            "DOL starter operation"
            if starter_kind in ["dol", "dol_adv"]
            else f"{device_type} operation"
        ),
        "protection trips",
        "local/remote control interface",
    ]

    if comm_mode != "hardwired":
        if has_plc:
            sat_items.append(f"{comm_label} communication with panel control devices")
        else:
            sat_items.append(
                f"{comm_label} interface availability and communication with the external control system where provided"
            )

    if starter_kind == "vfd":
        sat_items.extend(["pressure transmitter scaling", "pressure control stability"])

    if starter_kind == "dol_adv":
        sat_items.append("advanced motor-management alarm and trip verification")

    lines.append("3. SAT shall verify " + ", ".join(sat_items) + ".")

    content = "\n".join(lines)
    return content.encode("utf-8")
