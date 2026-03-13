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
        {"Field": "Configurations ID", "Value": twin.config_id}
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
             "Category": "Power Component",
             "Item": comp.item_category,
             "Qty": float(comp.qty),
             "Schneider Family (example)": "TeSys / Altivar",
             "Part No.": comp.part_number,
             "Key Selection Notes / Options": comp.description or "Standard component per motor power rating"
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
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_params.to_excel(writer, sheet_name='Parameters', index=False)
        df_bom.to_excel(writer, sheet_name='BOM-Template', index=False)
        df_io.to_excel(writer, sheet_name='IO-List', index=False)
        
    output.seek(0)
    return output.read()
