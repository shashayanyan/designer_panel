DESCRIPTION = """
The variable speed pump booster set is designed for automatic pressure or flow regulation in pumping applications requiring energy efficiency, process stability and flexible pump control.
Each pump is controlled by an Altivar Process ATV600 / ATV630 variable speed drive. The drive adjusts pump speed according to real system demand, typically using pressure, flow or level feedback. This solution is suitable for pressure boosting, water supply, HVAC, utility pumping and industrial process applications where stable pressure, reduced energy consumption and advanced diagnostics are required.
"""


TECHNICAL_CHARACTERISTICS = """
- Starting method: variable speed drive starting with adjustable acceleration and deceleration ramps.
- Pump operation: variable-speed operation.
- Drive range: Altivar Process ATV600 / ATV630.
- Power range: up to 55 kW, depending on motor rating, duty, overload requirements and cabinet thermal design.
- Reference configuration: {{PUMP_COUNT}} independent pump drives.
- Typical supply voltage: 3-phase, 380-480 V AC, 50/60 Hz.
- Control architecture: one variable speed drive per pump.
- Feedback signals: suitable for pressure, flow or level feedback using 0-10 V, 0-20 mA or 4-20 mA signals.
- Local control: Start / Stop pushbuttons and status indication on the cabinet door.
- Communication: possible integration with PLC, BMS, SCADA or higher-level systems through supported communication interfaces.
- Enclosure: {{MOUNTING_TYPE}} industrial {{MATERIAL}} enclosure, based on {{RANGE}} or equivalent.
- Thermal design: cabinet ventilation, spacing and derating to be validated according to installed drive power and ambient conditions.
"""


FUNCTIONS = """
- Smooth pump start and stop with adjustable acceleration and deceleration ramps.
- Variable speed control of each pump.
- Automatic pressure, flow or level regulation using analog feedback.
- Integrated PID control for maintaining the required process setpoint.
- Energy optimization by adapting pump speed to real demand.
- Local control from the cabinet door and remote control from PLC, BMS, SCADA or external control system.
- Communication of operating status, alarms, faults and measurements to a higher-level control system.
- Diagnostics and fault history available through the drive interface and/or supervision system.
- Possibility to implement duty/standby, cascade or multi-pump control when combined with suitable PLC or control logic.
"""


PROTECTIONS = """
- Motor overload protection.
- Electronic thermal protection of the motor and drive.
- Short-circuit protection of each pump feeder.
- Protection against overcurrent, undervoltage and overvoltage.
- Protection against input phase loss and motor phase loss.
- Protection against ground fault.
- Drive overheating protection.
- Safe Torque Off function available when correctly integrated into the safety circuit.
- Fault indication on the cabinet door and possible fault transmission to PLC, BMS or SCADA.
"""
