from io import BytesIO
from typing import Dict
import json
import os

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

    def format_worksheet(worksheet):
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

    def dfs_to_excel_bytes(dataframes: Dict[str, pd.DataFrame]) -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet_name, df in dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                format_worksheet(writer.sheets[sheet_name])
        output.seek(0)
        return output.read()

    def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
        return dfs_to_excel_bytes({"Sheet1": df})

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

        # Load hardware logic
        json_path = os.path.join(
            os.path.dirname(__file__),
            "added_hardware",
            "00_added_hardware_and_mode_logic.json",
        )
        try:
            with open(json_path, "r") as f:
                hardware_logic = json.load(f)
            hardware_map = {item["Circuit breaker"]: item for item in hardware_logic}
        except FileNotFoundError:
            hardware_map = {}

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

                # Apply hardware addition logic
                if line.part_number and line.part_number in hardware_map:
                    hw = hardware_map[line.part_number]
                    qty_per_cb = hw["Recommended qty per CB"]

                    # Add auxiliary
                    bom_data.append(
                        {
                            "Index": str(row_index),
                            "Item Category": "Auxiliary",
                            "Item": hw["OF auxiliary"],
                            "Qty": float(line.qty) * qty_per_cb,
                            "Part No.": hw["OF auxiliary"],
                            "Key Selection Notes / Options": hw["Notes"],
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

    # First load the json file of the selected series, if any of the relevant assets are chosen
    if (
        "IO List" in assets_flat
        or "IO" in assets_flat
        or "Alarm List" in assets_flat
        or "Alarms" in assets_flat
        or "Events" in assets_flat
        or "Event List" in assets_flat
    ):

        series_appendix = "dol.json"
        if twin.series_id == "DOL_ADV":
            series_appendix = "dola.json"
        elif twin.series_id == "SS":
            series_appendix = "ss.json"
        elif twin.series_id == "VSD" or twin.series_id == "VFD":
            series_appendix = "vsd.json"

        # Load hardware logic
        json_path = os.path.join(
            os.path.dirname(__file__), "io-alarms-events", series_appendix
        )
        try:
            with open(json_path, "r") as f:
                io_alarms_events = json.load(f)
        except FileNotFoundError:
            print(
                f"Warning: {series_appendix} not found. IO/Alarms/Events may be incomplete."
            )

        # --- 3. IO-List ---
        if "IO List" in assets_flat or "IO" in assets_flat:
            physical_io_list_per_motor = io_alarms_events["physicalIOListPerMotor"]
            io_dfs = {}

            digital_inputs = physical_io_list_per_motor.get("digitalInputs", [])
            if digital_inputs:
                io_dfs["Digital Inputs"] = pd.DataFrame(
                    [
                        {
                            "Tag": item["Signal tag"],
                            "Name": item["Signal name"],
                            "Direction": item["Direction"],
                            "Type": item["Type"],
                            "Source Device": item["Source device"],
                            "Notes": item["Basic notes"],
                        }
                        for item in digital_inputs
                    ]
                )

            digital_outputs = physical_io_list_per_motor.get("digitalOutputs", [])
            if digital_outputs:
                io_dfs["Digital Outputs"] = pd.DataFrame(
                    [
                        {
                            "Tag": item["Signal tag"],
                            "Name": item["Signal name"],
                            "Direction": item["Direction"],
                            "Type": item["Type"],
                            "Target Device": item["Target device"],
                            "Notes": item["Basic notes"],
                        }
                        for item in digital_outputs
                    ]
                )

            analog_io = physical_io_list_per_motor.get("analogIO", [])
            if analog_io:
                io_dfs["Analog IO"] = pd.DataFrame(
                    [
                        {
                            "Tag": item["Signal tag"],
                            "Name": item["Signal name"],
                            "Direction": item["Direction"],
                            "Type": item["Type"],
                            "Device": item["Source / target device"],
                            "Notes": item["Basic notes"],
                        }
                        for item in analog_io
                    ]
                )

            derived_signals = io_alarms_events.get("derivedInternalStatusSignals", [])
            if derived_signals:
                io_dfs["Derived Internal Status Signals"] = pd.DataFrame(
                    [
                        {
                            "Tag": item["Signal tag"],
                            "Name": item["Signal name"],
                            "Logic": item["Logic"],
                            "Notes": item["Notes"],
                        }
                        for item in derived_signals
                    ]
                )

            if io_dfs:
                generated_files[f"{asset_numbers['IO']}_IO-List.xlsx"] = (
                    dfs_to_excel_bytes(io_dfs)
                )

        # -- 4. Alarm List ---
        if "Alarm List" in assets_flat or "Alarms" in assets_flat:
            alarms = io_alarms_events.get("alarmList", [])
            if alarms:
                alarms_data = [
                    {
                        "Tag": item["Alarm tag"],
                        "Message": item["Alarm message"],
                        "Source": item["Source"],
                        "Basic Trigger Logic": item["Basic trigger logic"],
                    }
                    for item in alarms
                ]
                alarms_df = pd.DataFrame(alarms_data)
                generated_files[f"{asset_numbers['Alarms']}_Alarm_List.xlsx"] = (
                    df_to_excel_bytes(alarms_df)
                )

        if "Events" in assets_flat or "Event List" in assets_flat:
            # TBD
            series_appendix = "dol.json"
            if twin.series_id == "DOL_ADV":
                series_appendix = "dola.json"
            elif twin.series_id == "SS":
                series_appendix = "ss.json"
            elif twin.series_id == "VSD" or twin.series_id == "VFD":
                series_appendix = "vsd.json"

            # Load hardware logic
            json_path = os.path.join(
                os.path.dirname(__file__), "io-alarms-events", series_appendix
            )
            try:
                with open(json_path, "r") as f:
                    events = json.load(f)
                events_map = events["eventList"]
            except FileNotFoundError:
                events_map = {}

            print(f"Resolved {len(events_map)} events for series {twin.series_id}")
            print(f"Example event: {events_map[0] if events_map else 'N/A'}")

            events_data = [
                {
                    "Tag": item["Event tag"],
                    "Message": item["Event message"],
                    "Source / Trigger": item["Source / trigger"],
                }
                for item in events_map
            ]

            events_df = pd.DataFrame(
                events_data if events_data else [{"Status": "No events resolved"}]
            )
            generated_files[f"{asset_numbers['Events']}_Event_List.xlsx"] = (
                df_to_excel_bytes(events_df)
            )

    return generated_files
