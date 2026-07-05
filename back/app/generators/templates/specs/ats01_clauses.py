# Lower Soft Starter (ATS01) Specification Clauses

ats01_motor_feeders = [
    "Each pump motor shall be controlled by an individual Altistart 01 type soft starter suitable for {motor_power_kw} kW motor duty.",
    "The soft starter shall provide controlled voltage-ramp starting and stopping of asynchronous motors to reduce mechanical shock, hydraulic stress, and current peaks during pump operation.",
    "The soft starter shall comply with utilisation category AC-53B in accordance with EN/IEC 60947-4-2.",
    "The soft starter shall incorporate an integrated bypass function to reduce heat dissipation and operating noise after completion of the starting ramp.",
    "The soft starter shall provide adjustable acceleration and deceleration ramp times, configurable from 1 to 10 seconds.",
    "The soft starter shall provide adjustable starting torque from 30% to 80% of the motor direct-on-line starting torque.",
    "The soft starter shall include discrete logic inputs for stop, run, and boost-on-start functions, including a BOOST function for difficult starting conditions.",
    "The soft starter shall provide local status indication for starter power and nominal voltage reached, and shall provide an end-of-start signal for external control or monitoring.",
    "The soft starter shall be compact and suitable for DIN-rail or panel mounting, with side-by-side installation capability where permitted by the manufacturer.",
]

ats01_control_philosophy = [
    "Demand detection: start the lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Starting logic: apply a configurable voltage ramp to limit starting torque and current peaks while reducing mechanical and hydraulic stress on the pump system.",
    "Difficult-start handling: enable the boost-on-start function where required to overcome static friction or high breakaway torque during pump startup.",
    "Stopping logic: apply a configurable deceleration ramp where required to reduce hydraulic shock and support controlled pump stopping.",
    "Staging and de-staging logic: add pumps when the system cannot maintain pressure setpoint for a configurable time, and remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear across all pumps.",
    "Failure handling: if any pump/soft starter becomes unavailable, remaining pumps shall continue to operate within available capacity and generate an alarm.",
]
