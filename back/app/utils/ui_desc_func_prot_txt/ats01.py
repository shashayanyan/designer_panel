DESCRIPTION = """
The soft starter pump booster set is designed for pump applications where reduced mechanical and electrical stress during starting and stopping is required, while maintaining fixed-speed operation during normal running.
Each pump is started through an Altistart soft starter, which allows smoother acceleration compared with Direct-On-Line starting. This solution is suitable for pumping systems where direct starting could create high inrush current, pressure shocks, mechanical stress or water hammer, but where continuous speed regulation is not required.
"""


TECHNICAL_CHARACTERISTICS = """
- Starting method: soft starting by voltage ramp.
- Pump operation: fixed-speed operation after starting.
- Reference soft starter: Altistart 01, 22 A, 380-415 V.
- Control architecture: one soft starter per pump.
- Reference configuration: {{PUMP_COUNT}} independent pump feeders.
- Typical supply voltage: 3-phase, 380-415 V AC.
- Main components per pump: soft starter, magnetic motor circuit breaker, line contactor and thermal overload relay.
- Local control: Start / Stop pushbuttons on the cabinet door.
- Indication: Run and Trip/Fault pilot lights for each pump.
- Enclosure: {{MOUNTING_TYPE}} industrial {{MATERIAL}} enclosure, based on {{RANGE}} or equivalent.
- External control: possible connection to pressure switches, level switches, PLC, BMS or other control devices.
"""


FUNCTIONS = """
- Smooth pump starting with reduced starting current compared with Direct-On-Line starting.
- Reduction of mechanical stress on pumps, couplings and pipework during starting.
- Reduction of hydraulic shocks during pump start-up.
- Manual start and stop of each pump from the cabinet door.
- Remote start and stop from PLC, BMS, pressure switch, level switch or external controller.
- Fixed-speed pump operation after the start sequence.
- Individual control and indication for each pump.
- Possibility to implement duty/standby or simple pump sequencing through external control logic.
"""


PROTECTIONS = """
- Short-circuit protection of each pump feeder through a magnetic motor circuit breaker.
- Motor overload protection through a thermal overload relay.
- Protection against prolonged overcurrent conditions.
- Manual disconnection of each pump feeder through the motor circuit breaker.
- Electrical switching of each pump through the line contactor.
- Trip/Fault indication on the cabinet door.
- Protective earth connection for each outgoing motor cable.
- Possibility to integrate emergency stop or safety shutdown through an external safety circuit.
"""
