DESCRIPTION = """
The Direct-On-Line pump booster set is designed for fixed-speed operation of multiple pumps in water supply, pressure boosting, utility pumping and simple industrial pumping applications.
The system provides basic start/stop control of each pump through a contactor-based motor feeder. Each pump is controlled independently and protected by dedicated motor protection devices. This solution is suitable when variable speed regulation is not required and when the hydraulic network can accept direct motor starting and fixed-speed pump operation.
"""


TECHNICAL_CHARACTERISTICS = """
- Starting method: Direct-On-Line motor starting.
- Pump operation: fixed-speed operation.
- Control architecture: one motor feeder per pump.
- Reference configuration: {{PUMP_COUNT}} independent pump feeders.
- Typical supply voltage: 3-phase, 380-415 V AC, depending on local network.
- Main components per pump: magnetic motor circuit breaker, contactor and thermal overload relay.
- Local control: Start / Stop pushbuttons on the cabinet door.
- Indication: Run and Trip/Fault pilot lights for each pump.
- Enclosure: {{MOUNTING_TYPE}} industrial {{MATERIAL}} enclosure, based on {{RANGE}} or equivalent.
- External control: possible connection to pressure switches, level switches, PLC, BMS or other control devices.
"""


FUNCTIONS = """
- Manual start and stop of each pump from the cabinet door.
- Remote start and stop from PLC, BMS, pressure switch, level switch or external controller.
- Fixed-speed pump operation.
- Individual control and indication for each pump.
- Possibility to implement simple duty/standby operation through external control logic.
- Simple integration of permissive signals and basic interlocks.
- Robust and easy-to-maintain architecture for basic pumping applications.
"""


PROTECTIONS = """
- Short-circuit protection of each pump feeder through a magnetic motor circuit breaker.
- Motor overload protection through a thermal overload relay.
- Protection against prolonged overcurrent conditions.
- Manual disconnection of each pump feeder through the motor circuit breaker.
- Electrical switching of each pump through the contactor.
- Trip/Fault indication on the cabinet door.
- Protective earth connection for each outgoing motor cable.
- Possibility to integrate emergency stop or safety shutdown through an external safety circuit.
"""
