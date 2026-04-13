# Variable Speed Drive (VSD) Specification Clauses

vsd_motor_feeders = [
    "Each pump motor shall be controlled by an individual Variable Speed Drive (VSD) suitable for {motor_power_kw} kW motor duty.",
    "The drive shall control motor speed over the full specified operating range with static speed accuracy better than or equal to ±0.5% of rated speed. [cite: 469]",
    "The drive shall include an automatic energy-optimisation mode that continuously adjusts motor flux based on measured speed and load to minimise losses. [cite: 477]",
    "The VSD shall ride through three-phase supply voltage dips up to 20% of nominal voltage for any duration with reduced output power and without tripping. [cite: 528]"
]

vsd_control_philosophy = [
    "Demand detection: start lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Speed control: modulate lead pump speed via PID loop to maintain discharge pressure setpoint.",
    "Staging logic: add pumps when the system cannot maintain setpoint (e.g., lead speed above a configurable threshold for a configurable time).",
    "De-staging logic: remove pumps when demand decreases (e.g., average speed below a configurable threshold for a configurable time) while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear.",
    "Failure handling: if any pump/drive becomes unavailable, remaining pumps shall continue to control pressure within available capacity and generate an alarm."
]