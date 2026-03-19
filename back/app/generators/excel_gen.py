import pandas as pd
from io import BytesIO
from ..schemas.configurator import DigitalTwinResponse

def generate_excel_from_twin(twin: DigitalTwinResponse) -> bytes:
    """
    Takes a unified Digital Twin 'DNA' response and translates it into 
    the Application Pack standard multi-sheet Excel file.
    Returns the Excel file as a raw byte stream (BytesIO).
    """
    
    # --- 1. Parameters Sheet ---
    # Map high level metadata from the twin
    parameters_data = [
        {"Field": "Application", "Value": "Water Booster Set"},  # Example static / inferred
        {"Field": "Starter Type", "Value": {"DOL": "Direct-On-Line", "YD": "Star-Delta", "VFD": "Variable Speed Drive"}.get(twin.series_id, twin.series_id)},
        {"Field": "Motor Power (each)", "Value": f"{twin.motor_power_kw} kW"},
        {"Field": "Quantity", "Value": f"{twin.load_count} pumps"},
        {"Field": "Enclosure", "Value": f"{twin.enclosure.dimensions_mm} - {twin.enclosure.mounting_type}"},
        {"Field": "Configurations ID", "Value": twin.config_id},
        {"Field": "Bypass Strategy", "Value": twin.bypass_strategy or "N/A"}
    ]
    df_params = pd.DataFrame(parameters_data)
    
    # --- 2. BOM Template Sheet ---
    # Combine Enclosure, Power Components, and Accessories
    bom_data = []

    # Enclosure
    bom_data.append({
        "Category": "Enclosure",
        "Item": f"Enclosure {twin.enclosure.mounting_type}",
        "Qty": 1,
        "Schneider Family (example)": "Spacial / Universal enclosure family",
        "Part No.": twin.enclosure.catalog_ref,
        "Key Selection Notes / Options": f"Dimensions: {twin.enclosure.dimensions_mm}"
    })
    
    # Components
    for comp in twin.components:
         bom_data.append({
             "Category": comp.item_category,
             "Item": comp.description or comp.item_category,
             "Qty": float(comp.qty),
             "Schneider Family (example)": "TeSys / Altivar",
             "Part No.": comp.part_number,
             "Key Selection Notes / Options": "Standard component per motor power rating"
         })

    if getattr(twin, 'bypass_contactor_part_number', None):
         bom_data.append({
             "Category": "Bypass Contactor",
             "Item": "Bypass Contactor",
             "Qty": float(twin.load_count),
             "Schneider Family (example)": "TeSys",
             "Part No.": twin.bypass_contactor_part_number,
             "Key Selection Notes / Options": twin.bypass_strategy
         })

    # Accessories
    for acc in twin.accessories:
         bom_data.append({
             "Category": acc.category or "Accessory",
             "Item": "Optional Accessory",
             "Qty": float(acc.qty),
             "Schneider Family (example)": "Various",
             "Part No.": acc.part_number,
             "Key Selection Notes / Options": acc.description or ""
         })

    df_bom = pd.DataFrame(bom_data)
    
    # --- 3. IO-List Sheet ---
    # Generate a dummy / starter IO list dynamically based on pump counts
    io_data = []
    # Base IO (System level)
    io_data.append({"Tag": "ESD-01", "Description": "Emergency stop (panel)", "Equipment": "Booster Panel", "Signal Type": "DI", "Interface": "Hardwired", "Normal": "Closed", "PLC Destination": "DI Module", "Alarm?": "Y"})
    
    # Pump Level IO
    for i in range(1, twin.load_count + 1):
        io_data.extend([
             {"Tag": f"RUNCMD-P{i}", "Description": f"Run command Pump {i}", "Equipment": f"Pump {i}", "Signal Type": "CMD", "Interface": "Modbus TCP", "Normal": "", "PLC Destination": f"Drive #{i} Control Word", "Alarm?": "N"},
             {"Tag": f"STATUS-P{i}", "Description": f"Drive status Pump {i}", "Equipment": f"Pump {i}", "Signal Type": "FB", "Interface": "Modbus TCP", "Normal": "", "PLC Destination": f"Drive #{i} Status Word", "Alarm?": "Y"},
             {"Tag": f"FAULT-P{i}", "Description": f"Drive fault code Pump {i}", "Equipment": f"Pump {i}", "Signal Type": "FB", "Interface": "Modbus TCP", "Normal": "", "PLC Destination": f"Drive #{i} Fault Code", "Alarm?": "Y"},
        ])
    df_io = pd.DataFrame(io_data)
    
    # --- Export to BytesIO using ExcelWriter ---
    output = BytesIO()
    assets = twin.selected_assets or []
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Always include parameters if Excel is being generated
        df_params.to_excel(writer, sheet_name='Parameters', index=False)
        
        # Prepare assets for case-insensitive matching
        assets = [a.lower().strip() for a in (twin.selected_assets or [])]

        # Legacy/Standard Sheets
        if not assets or "bill of materials" in assets:
            df_bom.to_excel(writer, sheet_name='BOM-Template', index=False)
            
        if not assets or "data sheet" in assets: # Assuming IO-List falls logically under data sheet definition
            df_io.to_excel(writer, sheet_name='IO-List', index=False)
            
            # Application Data Sheets using Master Data
            network_data = [
                {"Tag": item.tag, "Description": item.description, "Signal Type": item.signal_type, 
                 "Interface": item.interface, "IP Address": item.ip_address or "N/A"}
                for item in twin.network_plan
            ]
            df_network = pd.DataFrame(network_data if network_data else [{"Status": "No network IO points resolved"}])
            df_network.to_excel(writer, sheet_name='Network-IP-Plan', index=False)

            alarm_data = [
                {"Code": item.code, "Source Tag": item.source_tag, "Condition": item.condition, 
                 "Priority": item.priority, "Message": item.operator_message}
                for item in twin.alarm_list
            ]
            df_alarm = pd.DataFrame(alarm_data if alarm_data else [{"Status": "No alarms resolved"}])
            df_alarm.to_excel(writer, sheet_name='Alarm_List', index=False)

            option_data = [
                {"Category": item.category, "Option Name": item.name, "Type": "Base" if item.is_base else "Optional", 
                 "Specification Hint": item.spec_text, "Notes": item.engineering_notes}
                for item in twin.option_matrix
            ]
            df_option = pd.DataFrame(option_data if option_data else [{"Status": "No options resolved"}])
            df_option.to_excel(writer, sheet_name='Option-Matrix', index=False)
        
    output.seek(0)
    return output.read()
