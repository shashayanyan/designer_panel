# DOL Specification Clauses

dol_motor_feeders = [
    "Each pump motor shall be controlled by an individual Direct-On-Line (DOL) starter suitable for {motor_power_kw} kW motor duty.",
    "The starter assembly shall comprise, as a minimum, one 3-pole switching device and one short-circuit protective device, with overload protection provided either by a thermal overload relay or by a thermal-magnetic motor circuit breaker. [cite: 38]",
    "The starter shall provide non-reversing direct-on-line starting and stopping of one three-phase squirrel-cage induction motor in utilization category AC-3 at 50/60 Hz. [cite: 37]",
    "The starter shall be designed so that restoration of motor operation after an overload or undervoltage trip requires a deliberate reset or deliberate restart action. [cite: 55]"
]

dol_control_philosophy = [
    "Demand detection: start lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Staging logic: add pumps when the system cannot maintain setpoint for a configurable time.",
    "De-staging logic: remove pumps when demand decreases while maintaining stable pressure.",
    "Anti-short-cycle: minimum run time and minimum stop time shall be implemented for each pump.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear.",
    "Failure handling: if any pump/starter becomes unavailable, remaining pumps shall continue to control pressure within available capacity and generate an alarm."
]