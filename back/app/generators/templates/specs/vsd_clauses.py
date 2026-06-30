# Variable Speed Drive (VSD) Specification Clauses

vsd_motor_feeders = [
    "Each pump motor shall be controlled by an individual Variable Speed Drive (VSD) suitable for {motor_power_kw} kW motor duty.",
    "The drive shall control motor speed over the full specified operating range with static speed accuracy better than or equal to ±0.5% of rated speed.",
    "The drive shall include an automatic energy-optimisation mode that continuously adjusts motor flux based on measured speed and load to minimise losses.",
    "The VSD shall ride through three-phase supply voltage dips up to 20% of nominal voltage for any duration with reduced output power and without tripping.",
    "The drive shall comply with environmental categories 3C3 and 3S3 as defined in IEC/EN 60721.",
    "The drive shall operate at full rated power up to 50 °C without derating, with extended operating capability up to 60 °C.",
    "The drive shall be capable of operating at altitudes up to 4,800 m above sea level and shall apply only the derating factors provided by the manufacturer.",
    "The drive shall include native Ethernet connectivity for fast integration into automation architectures, with protocol support provided according to the selected communication configuration.",
    "The drive shall provide Safe Torque Off (STO) as a standard integrated safety function, certified in accordance with IEC 61800-5-2 and compliant with SIL3 (EN/IEC 62061) and PL e (EN/ISO 13849-1).",
]

vsd_control_philosophy = [
    "Demand detection and speed control: modulate the lead pump speed via PID loop to maintain discharge pressure setpoint and start the lead pump when pressure falls below setpoint by a configurable margin or when demand is otherwise detected.",
    "Staging and de-staging logic: add pumps when the system cannot maintain setpoint, such as lead speed above a configurable threshold for a configurable time, and remove pumps when demand decreases while maintaining stable pressure.",
    "Alternation: lead/lag assignment shall rotate automatically based on runtime to equalize wear across all pumps.",
    "Energy monitoring: the drive shall log energy consumption and operating hours and shall present daily, weekly, monthly, and yearly energy trends with accuracy better than ±5% of measured kW.",
    "Pump performance assistance: the drive shall include an embedded pump curve function displaying real-time operating points against the pump characteristic curve, and shall display a dynamic QR code whenever a fault occurs to identify the fault and link to the corresponding troubleshooting information.",
    "Multi-pump resilience: the drive shall support a redundant master function in a multi-pump architecture via Ethernet, ensuring continuous operation in case of master drive failure; an additional Ethernet communication board shall be provided when required.",
    "Maintenance and replacement: the drive shall provide built-in predictive maintenance capabilities, activated through licensing, enabling predictive monitoring of both the drive and pump without external sensors or a learning phase, and shall support Fast Device Replacement (FDR) via Ethernet to automatically restore the complete configuration to a replacement drive using the assigned device name.",
]
