# DOL Specification Clauses

dol_motor_feeders = [
    "Each pump motor shall be controlled by an individual Direct-On-Line (DOL) motor starter suitable for {motor_power_kw} kW motor duty.",
    "Each DOL feeder shall include a TeSys Deca type line contactor rated for AC-3 motor switching duty and selected according to the motor full-load current and utilisation category.",
    "Each feeder shall include short-circuit protection, isolation, and motor overload protection using a coordinated motor circuit breaker and/or overload relay arrangement suitable for the selected motor rating.",
    "The motor protection device shall provide manual isolation, manual motor control, and short-circuit and thermal protection in a compact starter assembly where applicable.",
    "The starter combination shall be selected using manufacturer-tested coordination tables and shall support Type 1 or Type 2 coordination according to the project short-circuit level and availability requirements.",
    "The contactor shall provide mechanically linked and mirror auxiliary contacts suitable for safety, permissive, and feedback circuits where required.",
    "The starter shall support direct hardwired or PLC-based control using a control coil voltage matched to the selected control architecture, with surge suppression provided where required.",
    "The starter assembly shall use maintenance-reducing connection technology, including EverLink, spring, or multi-standard screw terminals where available for the selected frame size.",
    "The feeder shall provide run, fault, trip, ready, and local/remote interface signals through auxiliary contacts and overload or circuit-breaker trip indication where required by the selected control architecture.",
]

dol_control_philosophy = [
    "Demand detection: start the lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting logic: energize the selected pump contactor only when all electrical, mechanical, and process permissives are healthy.",
    "Stopping logic: de-energize the selected pump contactor when demand is satisfied, a stop command is issued, or a protective trip or emergency stop condition occurs.",
    "Staging and de-staging logic: add pumps when the system cannot maintain pressure setpoint for a configurable time, and remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime or number of starts to equalize wear across all pumps.",
    "Protection handling: motor overload, short-circuit trip, contactor feedback mismatch, phase loss where monitored, or emergency stop shall inhibit the affected pump and generate an alarm.",
    "Failure handling: if any pump/starter becomes unavailable, remaining pumps shall continue to operate within available capacity and generate an alarm.",
]
