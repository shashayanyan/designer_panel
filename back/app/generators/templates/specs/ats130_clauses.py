ats130_motor_feeders = [
    "Each pump motor shall be controlled by an individual Altivar Soft Starter ATS130 type soft starter suitable for {motor_power_kw} kW motor duty.",
    "The soft starter shall provide controlled soft start and soft stop functions for asynchronous motors to reduce mechanical stress, hydraulic shock, and electrical starting current peaks.",
    "The soft starter shall comply with utilisation category AC-53A in accordance with EN/IEC 60947-4-2.",
    "The soft starter shall be suitable for operation on three-phase motor supplies from 200 V to 480 V AC.",
    "The soft starter shall provide a high starting capability as standard, with overload capacity suitable for 300% of rated operational current for 5 seconds.",
    "The starter shall include an internal bypass function to reduce heat dissipation and operating losses after completion of the starting ramp.",
    "The starter shall include deceleration voltage ramp and boost functions to support controlled stopping and difficult starting conditions.",
    "The starter shall include built-in protection monitoring for mains phase failure, starter thermal condition, bypass error, and control-voltage availability.",
    "The starter shall use 24 V DC control supply and shall provide PLC-compatible digital inputs, including run/stop control and boost-on-start command.",
    "The starter shall provide relay and digital output signalling for external control, status, and fault indication.",
    "The starter shall use maintenance-reducing power and control terminations, including Everlink-type power terminals and spring control terminals, eliminating the requirement for annual terminal retightening where installed according to manufacturer instructions.",
    "The starter shall support compact panel integration by DIN-rail or backplate mounting, side-by-side installation where permitted, and direct mechanical coordination with the associated TeSys Deca motor protection device.",
]

ats130_control_philosophy = [
    "Demand detection: start the lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting logic: apply a controlled soft-start ramp to limit current peaks and reduce mechanical and hydraulic stress on the pump system.",
    "Difficult-start handling: enable the boost-on-start function where required to overcome static friction, high breakaway torque, or adverse pump starting conditions.",
    "Stopping logic: apply a controlled deceleration ramp where required to reduce hydraulic shock and support smooth pump stopping.",
    "Staging and de-staging logic: add pumps when the system cannot maintain pressure setpoint for a configurable time, and remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear across all pumps.",
    "Failure handling: if any pump/starter becomes unavailable or reports a starter, phase, bypass, thermal, or control-voltage fault, remaining pumps shall continue to operate within available capacity and generate an alarm.",
]
