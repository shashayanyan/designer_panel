dol_advanced_motor_feeders = [
    "Each pump motor shall be controlled by an individual Direct-On-Line (DOL) starter with advanced motor management suitable for {motor_power_kw} kW motor duty.",
    "Each DOL starter shall include a coordinated magnetic circuit breaker, line contactor, and advanced motor management controller selected according to the motor full-load current and duty requirements.",
    "The DOL starter shall provide direct-on-line motor switching with advanced electronic motor protection, monitoring, diagnostics, and control through the motor management controller.",
    "The motor management controller shall provide solid-state motor protection functions including overload, phase imbalance, phase loss, ground fault where configured, and thermal protection based on measured motor operating conditions.",
    "The motor management controller shall measure three-phase motor current and shall support motor temperature, ground-current, and voltage/power/energy monitoring where the required sensors or expansion modules are included.",
    "The DOL starter shall provide configurable alarms and trips to support early warning, fault prevention, and faster diagnosis of abnormal pump or motor operating conditions.",
    "The starter combination shall be selected using manufacturer-tested coordination tables and shall support Type 1 or Type 2 coordination according to the project short-circuit level and availability requirements.",
    "The contactor shall provide mechanically linked and mirror auxiliary contacts suitable for safety, permissive, and feedback circuits where required.",
    "The motor management controller shall provide discrete inputs and outputs for local/remote control, run command, status feedback, trip signalling, reset, permissives, and fault management.",
    "The DOL starter shall support integration into the selected control architecture through hardwired I/O and/or the selected communication interface, without changing the basic feeder protection and contactor arrangement.",
    "The DOL starter assembly shall use maintenance-reducing connection technology, including spring, cage-clamp, or multi-standard screw terminals where available for the selected frame size.",
]

dol_advanced_control_philosophy = [
    "Demand detection: start the lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting logic: energize the selected pump contactor only when all electrical, mechanical, process, protection, and motor-management permissives are healthy.",
    "Stopping logic: de-energize the selected pump contactor when demand is satisfied, a stop command is issued, or a protective trip, motor-management trip, or emergency stop condition occurs.",
    "Staging and de-staging logic: add pumps when the system cannot maintain pressure setpoint for a configurable time, and remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime or number of starts to equalize wear across all pumps.",
    "Advanced protection handling: overload, phase loss, phase imbalance, ground fault where configured, thermal alarm, motor-management trip, contactor feedback mismatch, or emergency stop shall inhibit the affected pump and generate an alarm.",
    "Diagnostic handling: motor-management alarms, trips, measured current values, operating status, and runtime or start-count data shall be made available to the panel controller or external control system according to the selected architecture.",
    "Failure handling: if any pump/DOL starter becomes unavailable, remaining pumps shall continue to operate within available capacity and generate an alarm.",
]
