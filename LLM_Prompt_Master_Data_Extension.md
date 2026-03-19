# Master Data Enhancement Prompt: Application Deliverables

**Context Context for LLM:**
You have been generating and maintaining the advanced engineering `application_library_dol_ss_vsd_ats01_ats130_critical_products.xlsx` configuration document for a Motor Control Application Library. We have deployed the database and configuration rules you previously generated into a dynamic FastAPI backend.

**The Current State:**
The backend successfully resolves Physical Hardware rules (Enclosures, Components, Accessories) to generate a "Digital Twin". However, the system is now being expanded to generate standard engineering deliverables: **IO Lists, Alarm Lists, Network IP Plans, and Option Matrices**. 

**Your Objective:**
You must generate three (3) new comprehensive, comma-separated sheets (CSVs) to be added to the `application_library_dol_ss_vsd_ats01_ats130_critical_products.xlsx` workbook. These tabs will serve as the "Single Source of Truth" master data tables to instruct the backend Python scripts on how to generate the aforementioned documents generically for *any* Application Type.

**Crucial Engineering Rule (The "Is_Per_Load" Pattern):**
The database must not hardcode duplicate arrays for identical pumps. Instead, use an `is_per_load` boolean column. 
- If `is_per_load = FALSE`: The Python engine will generate ONE row for the system (e.g., Main Panel Emergency Stop, Main Panel Low Pressure Alarm).
- If `is_per_load = TRUE`: The Python engine will loop through the user's selected `load_count` (e.g., 3 Pumps) and dynamically inject the pump index into the string (e.g., if you write `RUNCMD-P{i}`, the backend will generate `RUNCMD-P1`, `RUNCMD-P2`, `RUNCMD-P3`).

---

## Task 1: Generate "Application_IO_Templates" Tab
This sheet defines what PLC Inputs/Outputs must be generated based on the configuration.

**Required Columns:**
1. `application_id`: (Always use `APP-WATER-BOOSTER` for this iteration).
2. `tag_template`: The IO Tag (e.g., `PT-DISCH-01`, `RUNCMD-P{i}`). Use `{i}` for iterating load indices.
3. `description`: Human-readable description.
4. `signal_type`: (DI, DO, AI, AO, CMD, FB).
5. `interface`: Hardwired vs Network (e.g., 'Hardwired', 'Modbus TCP').
6. `is_per_load`: (TRUE/FALSE) 
7. `required_communication_mode`: (Optional). If this IO only exists when the user selects a specific network, list it here (e.g., "ModbusTCP"). If blank, it's always included.
8. `alarm_linked`: (Y/N) Does this IO trigger an alarm?

*Provide at least 10 rows covering Main Pressure Transmitters, E-Stops, Start/Stop commands per pump, and Status feedbacks.*

---

## Task 2: Generate "Application_Alarm_Templates" Tab
This sheet defines the SCADA/HMI alarm configurations.

**Required Columns:**
1. `application_id`: (Use `APP-WATER-BOOSTER`).
2. `alarm_code_template`: (e.g., `ALM-001`, `ALM-1{i}0`).
3. `tag_source_template`: Which IO tag triggers this? (e.g., `PT-DISCH-01`, `FAULT-P{i}`).
4. `condition`: What raises the alarm? (e.g., "Signal fault / out of range", "Drive fault active").
5. `priority`: (P1, P2, P3).
6. `is_per_load`: (TRUE/FALSE).
7. `operator_message`: The HMI popup text.

*Provide at least 8 rows covering Low/High Pressure limits, general emergency stops, and individual Drive Faults per pump.*

---

## Task 3: Generate "Application_Option_Matrix" Tab
This sheet controls the commercial/technical "Option Matrix" deliverable, outlining what features are considered Base offering versus Optional add-ons.

**Required Columns:**
1. `application_id`: (Use `APP-WATER-BOOSTER`).
2. `option_category`: (e.g., "Enclosure", "Power Quality", "Cybersecurity").
3. `option_name`: (e.g., "IP rating (IP54)", "Line reactor").
4. `is_base_or_optional`: ("Base", "Optional", "Project-specific").
5. `spec_text_hint`: Boilerplate sentence the consultant/engineer can copy for this feature.
6. `engineering_notes`: Internal SI/Panel Builder notes.

*Provide at least 8 rows spanning standard Enclosure ratings, Line Reactors, Sleep Modes, and Ethernet uplinks.*

**Output Format Constraint:**
Please append the exact CSV data blocks for the 3 tabs requested above inside the previously generated `application_library_dol_ss_vsd_ats01_ats130_critical_products.xlsx` workbook. Do not invent columns outside of the required schemas. Ensure all `{i}` templates logically align with `is_per_load=TRUE`. Do not change the existing columns or rows or sheets in the workbook unless it is necessary for consistency between new and old sheets (in which case you must explicitly state the changes you are making and why).
