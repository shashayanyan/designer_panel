DESCRIPTION = """
The pump booster set based on Altivar Soft Starter ATS130 is designed for fixed-speed pump applications where smooth starting, reduced electrical stress and reduced mechanical stress are required.
Compared with a Direct-On-Line solution, the ATS130 allows the pump motor to start more progressively, helping to reduce inrush current, mechanical shocks and hydraulic stress in the pipework. Compared with a variable speed drive solution, it remains a simpler fixed-speed architecture and is suitable when continuous pressure or flow regulation by speed variation is not required.
This solution is suitable for pump booster sets, water supply systems, utility pumping and simple industrial pumping applications where a robust and compact soft-starting solution is required.
"""


TECHNICAL_CHARACTERISTICS = """
- Starting method: soft starting using Altivar Soft Starter ATS130.
- Pump operation: fixed-speed operation after the start sequence.
- Typical power range: suitable for pump motors up to 55 kW, depending on selected ATS130 rating and motor current.
- Typical supply voltage: 3-phase, 200-480 V AC, depending on selected reference and local network.
- Control architecture: one soft starter per pump.
- Reference configuration: {{PUMP_COUNT}} independent pump feeders.
- Main components per pump: ATS130 soft starter, motor circuit breaker, line contactor and motor overload protection according to project design.
- Local control: Start / Stop pushbuttons on the cabinet door.
- Indication: Run and Trip/Fault pilot lights for each pump.
- Enclosure: {{MOUNTING_TYPE}} industrial {{MATERIAL}} enclosure, based on {{RANGE}} or equivalent.
- External control: possible connection to PLC, BMS, pressure switch, level switch or external pump controller.
"""


FUNCTIONS = """
- Smooth pump start with reduced starting current compared with Direct-On-Line starting.
- Progressive acceleration of the motor to reduce mechanical stress on pump, coupling and pipework.
- Reduction of hydraulic shocks during pump start-up.
- Soft stop possible depending on configuration and application requirements.
- Manual start and stop of each pump from the cabinet door.
- Remote start and stop from PLC, BMS, pressure switch, level switch or external controller.
- Fixed-speed pump operation after the start sequence.
- Individual control and indication for each pump.
- Possibility to implement duty/standby or pump sequencing through external control logic.
"""


PROTECTIONS = """
- Short-circuit protection of each pump feeder through a suitable motor circuit breaker or upstream protective device.
- Motor overload protection according to selected protection architecture.
- Protection against prolonged overcurrent conditions.
- Reduction of electrical stress during motor starting.
- Reduction of mechanical stress during pump starting.
- Manual disconnection of each pump feeder through the motor circuit breaker or isolating device.
- Electrical switching of each pump through the line contactor.
- Trip/Fault indication on the cabinet door.
- Protective earth connection for each outgoing motor cable.
- Possibility to integrate emergency stop or safety shutdown through an external safety circuit.
"""
