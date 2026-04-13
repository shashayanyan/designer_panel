# Higher Soft Starter (ATS130) Specification Clauses

ats130_motor_feeders = [
    "Each pump motor shall be controlled by an individual two-phase control soft starter suitable for {motor_power_kw} kW motor duty. [cite: 316]",
    "The soft starter shall include an integrated bypass contactor that automatically closes upon completion of the starting ramp. [cite: 317]",
    "The starter shall reduce mechanical stress on the driven equipment during acceleration and deceleration. [cite: 311]",
    "The soft starter shall provide a 'Boost' function to apply a higher initial voltage for a short duration to overcome high static friction at startup. [cite: 348]"
]

ats130_control_philosophy = [
    "Demand detection: start lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting/Stopping Logic: apply configurable acceleration and deceleration voltage ramps to minimize mechanical stress. [cite: 343, 344]",
    "Staging logic: add pumps when the system cannot maintain setpoint for a configurable time.",
    "De-staging logic: initiate soft-stop ramp down when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear.",
    "Failure handling: if any pump/starter becomes unavailable, remaining pumps shall continue to control pressure within available capacity and generate an alarm."
]