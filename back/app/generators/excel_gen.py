from io import BytesIO
from typing import Dict

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from ..generators.asset_number_gen import generate_asset_numbers
from ..schemas.configurator import DigitalTwinResponse
from ..utils.assets import flatten_asset_ids


def generate_excel_from_twin(twin: DigitalTwinResponse) -> Dict[str, bytes]:
    """
    Takes a unified Digital Twin 'DNA' response and translates it into
    individual Excel files for each sheet.
    Returns a dictionary mapping filenames to raw byte streams.
    """
    generated_files = {}
    assets_flat = flatten_asset_ids(twin.selected_assets)
    asset_numbers = generate_asset_numbers(assets_flat)

    def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

            # Extract workbook and active sheet to apply formatting
            workbook = writer.book
            if workbook.sheetnames:
                worksheet = workbook[workbook.sheetnames[0]]

                # 1. Header Styling (Blue background, White text)
                header_fill = PatternFill(
                    start_color="2B579A", end_color="2B579A", fill_type="solid"
                )
                header_font = Font(bold=True, color="FFFFFF")
                header_alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )

                for cell in worksheet[1]:  # Row 1 is the header
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = header_alignment

                # 2. Auto-adapt Column Widths
                for col_cells in worksheet.columns:
                    first_cell = col_cells[0]
                    col_letter = first_cell.column_letter

                    max_len = 0
                    for cell in col_cells:
                        if cell.value is not None:
                            # Use newlines to calculate width if wrapped, otherwise just raw length
                            cell_text = str(cell.value)
                            lines = cell_text.split("\n")
                            max_len = max(max_len, max(len(line) for line in lines))

                    # Add a padding margin (buffer) to the max length
                    adjusted_width = max_len + 3
                    worksheet.column_dimensions[col_letter].width = adjusted_width

        output.seek(0)
        return output.read()

    # --- 1. Parameters ---
    if "Parameters" in assets_flat:
        parameters_data = [
            {"Field": "Application", "Value": "Water Booster Set"},
            {
                "Field": "Starter Type",
                "Value": twin.series_name,
            },
            {"Field": "Motor Power (each)", "Value": f"{twin.motor_power_kw} kW"},
            {"Field": "Quantity", "Value": f"{twin.load_count} pumps"},
            {"Field": "Configurations ID", "Value": twin.config_id},
            {
                "Field": "Enclosure - Dimensions",
                "Value": f"{twin.enclosure.dimensions_mm}",
            },
            {
                "Field": "Enclosure - Mounting",
                "Value": twin.enclosure.mounting_type,
            },
            {
                "Field": "Enclosure - Material",
                "Value": twin.enclosure.material,
            },
            {
                "Field": "Enclosure - IP Rating",
                "Value": twin.enclosure.ip_rating or "N/A",
            },
            {
                "Field": "Enclosure - IK Rating",
                "Value": twin.enclosure.ik_rating or "N/A",
            },
            {
                "Field": "Enclosure - Door Type",
                "Value": twin.enclosure.door_type or "N/A",
            },
            {
                "Field": "Communication",
                "Value": (
                    twin.communication if twin.communication != "No" else "Hardwired"
                ),
            },
            {"Field": "PLC", "Value": twin.plc_included},
            {"Field": "SCADA", "Value": twin.scada_included},
            {"Field": "Incomer Count", "Value": "1"},
        ]
        df_params = pd.DataFrame(parameters_data)
        generated_files[f"{asset_numbers['Parameters']}_Parameters.xlsx"] = (
            df_to_excel_bytes(df_params)
        )

    # --- 2. BOM Template ---
    if "BOM" in assets_flat:
        row_index = 1
        bom_data = []

        # Exclusively database defined BOM Lines driven logically from resolved configuration
        if twin.bom_lines:
            for line in twin.bom_lines:
                bom_data.append(
                    {
                        "Index": str(row_index),
                        "Item Category": line.item_category,
                        "Item": line.item,
                        "Qty": float(line.qty),
                        "Part No.": line.part_number,
                        "Key Selection Notes / Options": (
                            line.key_selection_notes or "-"
                        ),
                    }
                )
                row_index += 1

        df_bom = pd.DataFrame(
            bom_data,
            columns=[
                "Index",
                "Item Category",
                "Item",
                "Qty",
                "Part No.",
                "Key Selection Notes / Options",
            ],
        )
        generated_files[f"{asset_numbers['BOM']}_BOM-Template.xlsx"] = (
            df_to_excel_bytes(df_bom)
        )

    # --- 3. IO-List ---
    if "IO List" in assets_flat or "IO" in assets_flat:
        io_data = []
        io_data.append(
            {
                "Tag": "ESD-01",
                "Description": "Emergency stop (panel)",
                "Equipment": "Booster Panel",
                "Signal Type": "DI",
                "Interface": "Hardwired",
                "Normal": "Closed",
                "PLC Destination": "DI Module",
                "Alarm?": "Y",
            }
        )

        for i in range(1, twin.load_count + 1):
            io_data.extend(
                [
                    {
                        "Tag": f"RUNCMD-P{i}",
                        "Description": f"Run command Pump {i}",
                        "Equipment": f"Pump {i}",
                        "Signal Type": "CMD",
                        "Interface": "Modbus TCP",
                        "Normal": "",
                        "PLC Destination": f"Drive #{i} Control Word",
                        "Alarm?": "N",
                    },
                    {
                        "Tag": f"STATUS-P{i}",
                        "Description": f"Drive status Pump {i}",
                        "Equipment": f"Pump {i}",
                        "Signal Type": "FB",
                        "Interface": "Modbus TCP",
                        "Normal": "",
                        "PLC Destination": f"Drive #{i} Status Word",
                        "Alarm?": "Y",
                    },
                    {
                        "Tag": f"FAULT-P{i}",
                        "Description": f"Drive fault code Pump {i}",
                        "Equipment": f"Pump {i}",
                        "Signal Type": "FB",
                        "Interface": "Modbus TCP",
                        "Normal": "",
                        "PLC Destination": f"Drive #{i} Fault Code",
                        "Alarm?": "Y",
                    },
                ]
            )
        df_io = pd.DataFrame(io_data)
        generated_files[f"{asset_numbers['IO']}_IO-List.xlsx"] = df_to_excel_bytes(
            df_io
        )

    if "Network Plan" in assets_flat or "Network" in assets_flat:
        network_data = [
            {
                "Tag": item.tag,
                "Description": item.description,
                "Signal Type": item.signal_type,
                "Interface": item.interface,
                "IP Address": item.ip_address or "N/A",
            }
            for item in twin.network_plan
            if (item.interface or "").strip().lower() != "hardwired"
        ]
        df_network = pd.DataFrame(
            network_data
            if network_data
            else [{"Status": "No network IO points resolved"}]
        )
        generated_files[f"{asset_numbers['Network']}_Network-IP-Plan.xlsx"] = (
            df_to_excel_bytes(df_network)
        )

    if "Alarm List" in assets_flat or "Alarms" in assets_flat:
        alarm_data = [
            {
                "Code": item.code,
                "Source Tag": item.source_tag,
                "Condition": item.condition,
                "Priority": item.priority,
                "Message": item.operator_message,
            }
            for item in twin.alarm_list
        ]
        df_alarm = pd.DataFrame(
            alarm_data if alarm_data else [{"Status": "No alarms resolved"}]
        )
        generated_files[f"{asset_numbers['Alarms']}_Alarm_List.xlsx"] = (
            df_to_excel_bytes(df_alarm)
        )

    return generated_files
