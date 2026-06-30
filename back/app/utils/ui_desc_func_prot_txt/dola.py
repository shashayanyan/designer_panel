DESCRIPTION = """
The advanced Direct-On-Line pump booster set is designed for fixed-speed operation of multiple pumps in water supply, pressure boosting, utility pumping and industrial pumping applications.
Each pump is controlled through an individual contactor-based motor feeder and protected by LTMR motor management controller instead of a conventional thermal overload relay. This provides electronic motor protection, diagnostics, alarm/trip management and easier integration with PLC, BMS or SCADA systems.
"""


TECHNICAL_CHARACTERISTICS = """
- Starting method: Direct-On-Line motor starting.
- Pump operation: fixed-speed operation.
- Control architecture: one motor feeder per pump.
- Reference configuration: {{PUMP_COUNT}} independent pump feeders.
- Typical supply voltage: 3-phase, 380-415 V AC.
- Main components per pump: magnetic motor circuit breaker, contactor and TeSys T LTMR motor management controller.
- Protection Technology: Protection technology: electronic motor protection and monitoring.
- Monitoring: Monitoring: motor current, current imbalance, overload, phase loss and fault status, depending on LTMR configuration.
- Communication: possible connection to PLC, BMS or SCADA through the selected LTMR communication interface.
- Local control: Start / Stop pushbuttons on the cabinet door.
- Indication: Run and Trip/Fault pilot lights for each pump.
- Enclosure: {{MOUNTING_TYPE}} industrial {{MATERIAL}} enclosure, based on {{RANGE}} or equivalent.
"""


FUNCTIONS = """
- Manual and remote start/stop of each pump.
- Individual control, protection and indication for each pump.
- Fixed-speed pump operation.
- Electronic overload protection and motor status monitoring.
- Alarm and trip management for each motor feeder.
- Remote transmission of pump status, run state, alarm state and trip state to PLC, BMS or SCADA.
- Possibility to implement duty/standby, duty-assist or pump alternation logic through an external controller.
- Improved diagnostics and easier maintenance compared with a conventional thermal overload relay solution.
"""


PROTECTIONS = """
- Short-circuit protection through a magnetic motor circuit breaker.
- Electronic overload protection.
- Protection against prolonged overcurrent conditions.
- Phase loss and current imbalance detection, depending on configuration.
- Earth-fault / ground-fault detection, depending on configuration.
- Trip/Fault indication on the cabinet door.
- Remote alarm and trip indication to PLC, BMS or SCADA.
- Protective earth connection for each outgoing motor cable.
- Possibility to integrate emergency stop or safety shutdown through an external safety circuit.
"""
