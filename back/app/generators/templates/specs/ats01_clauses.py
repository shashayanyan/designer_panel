# Lower Soft Starter (ATS01) Specification Clauses

ats01_motor_feeders = [
    "Each pump motor shall be controlled by an individual soft starter providing controlled voltage ramp-up suitable for {motor_power_kw} kW motor duty. [cite: 186]",
    "The soft starter shall limit motor starting torque and current peaks during motor acceleration. [cite: 190]",
    "The soft starter shall incorporate an internal bypass relay to shunt the power semiconductors after the motor has reached nominal speed. [cite: 195]",
    "The starter shall accept a discrete input signal to initiate a run command and a discrete input signal to initiate a stop command. [cite: 226, 227]"
]

ats01_control_philosophy = [
    "Demand detection: start lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting Logic: initiate soft start voltage ramp-up to minimize mechanical and electrical shock.",
    "Staging logic: add pumps when the system cannot maintain setpoint for a configurable time.",
    "De-staging logic: remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear.",
    "Failure handling: if any pump/starter becomes unavailable, remaining pumps shall continue to control pressure within available capacity and generate an alarm."
]