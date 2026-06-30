def get_asset_number(asset_index: int) -> str:
    if asset_index < 10:
        return f"00{asset_index}"
    return f"0{asset_index}"


def generate_asset_numbers(selected_assets: list[str]) -> dict[str, str]:
    base_index = 3
    asset_numbers = {}
    if "Parameters" in selected_assets:
        asset_numbers["Parameters"] = get_asset_number(base_index)
        base_index += 1

    if "BOM" in selected_assets:
        asset_numbers["BOM"] = get_asset_number(base_index)
        base_index += 1

    if "IO" in selected_assets:
        asset_numbers["IO"] = get_asset_number(base_index)
        base_index += 1

    if "Alarms" in selected_assets:
        asset_numbers["Alarms"] = get_asset_number(base_index)
        base_index += 1

    if "Events" in selected_assets or "Event List" in selected_assets:
        asset_numbers["Events"] = get_asset_number(base_index)
        base_index += 1

    if "Multi Line Diagram" in selected_assets:
        """
        account for svg and png format
        """
        asset_numbers["MLD-svg"] = get_asset_number(base_index)
        asset_numbers["MLD-png"] = get_asset_number(base_index + 1)
        asset_numbers["RefArch"] = get_asset_number(base_index + 2)
        base_index += 3

    if "Specification" in selected_assets:
        """
        account for docx and txt format
        """
        asset_numbers["spec-docx"] = get_asset_number(base_index)
        asset_numbers["spec-txt"] = get_asset_number(base_index + 1)
        base_index += 2

    if "BIM Object" in selected_assets:
        asset_numbers["BIM-logical"] = get_asset_number(base_index)
        asset_numbers["BIM-visual"] = get_asset_number(base_index + 1)
        base_index += 2

    return asset_numbers
