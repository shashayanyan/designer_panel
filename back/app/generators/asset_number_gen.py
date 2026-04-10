def get_asset_number(asset_index: int) -> str:
    if asset_index < 10:
        return f"00{asset_index}"
    return f"0{asset_index}"

def generate_asset_numbers(selected_assets: list) -> dict[str, str]:
    base_index = 4
    asset_numbers = {}
    if "Data Sheet" in selected_assets: 
        asset_numbers["Parameters"] = get_asset_number(base_index)
        asset_numbers["BOM"] = get_asset_number(base_index+1)
        asset_numbers["IO"] = get_asset_number(base_index+2)
        asset_numbers["Network"] = get_asset_number(base_index+3)
        asset_numbers["Alarms"] = get_asset_number(base_index+4)
        asset_numbers["Options"] = get_asset_number(base_index+5)
        base_index += 6

    if "Multi Line Diagram" in selected_assets:
        """
        account for svg and png format
        """
        asset_numbers["MLD-svg"] = get_asset_number(base_index)
        asset_numbers["MLD-png"] = get_asset_number(base_index+1)
        base_index += 3

    if "Specification" in selected_assets:
        """
        account for docx and txt format
        """
        asset_numbers["spec-docx"] = get_asset_number(base_index)
        asset_numbers["spec-txt"] = get_asset_number(base_index+1)
        base_index += 2

    if "BIM Object" in selected_assets:
        asset_numbers["BIM-logical"] = get_asset_number(base_index)
        asset_numbers["BIM-visual"] = get_asset_number(base_index+1)
        base_index += 2


    return asset_numbers