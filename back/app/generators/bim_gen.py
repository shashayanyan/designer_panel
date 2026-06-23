import argparse
import json

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry

# Explicit API imports (required in 0.8+)
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.style
import ifcopenshell.api.system
import ifcopenshell.api.type
import ifcopenshell.api.unit
import numpy as np

# ------------------------------------------------------------
# Helpers & Maps
# ------------------------------------------------------------

IFC_CLASS_MAP = {
    "Soft Starter": "IfcMotorConnection",
    "Magnetic CB": "IfcProtectiveDevice",
    "Line Contactor": "IfcSwitchingDevice",
    "Overload": "IfcProtectiveDevice",
    "Start PB": "IfcSwitchingDevice",
    "Stop PB": "IfcSwitchingDevice",
    "Pilot Light": "IfcLightFixture",
    "Power Terminal": "IfcJunctionBox",
    "Control Terminal": "IfcJunctionBox",
    "Power PE Terminal": "IfcJunctionBox",
    "Control PE Terminal": "IfcJunctionBox",
    "Power Cable Gland": "IfcDiscreteAccessory",
    "Control Cable Gland": "IfcDiscreteAccessory",
}


def create_color_style(model, name, r, g, b, transparency=0.0):
    """Creates an IFC Surface Style. Transparency is 0.0 (opaque) to 1.0 (invisible)."""
    style = ifcopenshell.api.style.add_style(model, name=name)
    ifcopenshell.api.style.add_surface_style(
        model,
        style=style,
        ifc_class="IfcSurfaceStyleRendering",
        attributes={
            "SurfaceColour": {
                "Name": None,
                "Red": float(r),
                "Green": float(g),
                "Blue": float(b),
            },
            "Transparency": float(transparency),
        },
    )
    return style


def create_clearance_zone(
    model, context, panel, name, width, depth, height, x, y, z, color_style
):
    """Creates an industry-standard PROVISIONFORSPACE clash detection zone."""
    proxy = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcBuildingElementProxy", name=name
    )
    if hasattr(proxy, "PredefinedType"):
        proxy.PredefinedType = "PROVISIONFORSPACE"
    proxy.Description = "Electrical Clearance / Maintenance Zone"

    ifcopenshell.api.aggregate.assign_object(
        model, products=[proxy], relating_object=panel
    )
    rep = create_box_representation(model, context, width, depth, height)
    ifcopenshell.api.geometry.assign_representation(
        model, product=proxy, representation=rep
    )

    if color_style:
        ifcopenshell.api.style.assign_item_style(
            model, item=rep.Items[0], style=color_style
        )

    matrix = np.eye(4)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z
    ifcopenshell.api.geometry.edit_object_placement(model, product=proxy, matrix=matrix)

    return proxy


def mm_to_m(v_mm):
    return v_mm / 1000.0


def load_data(path="002_DigitalTwin_DNA_CFG-SS011-2X.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_pset(model, product, name, properties):
    clean_properties = {k: v for k, v in properties.items() if v is not None}
    pset = ifcopenshell.api.pset.add_pset(model, product=product, name=name)
    ifcopenshell.api.pset.edit_pset(model, pset=pset, properties=clean_properties)
    return pset


def create_box_representation(model, context, width, depth, height):
    vertices = [
        [
            (0, 0, 0),
            (width, 0, 0),
            (width, depth, 0),
            (0, depth, 0),
            (0, 0, height),
            (width, 0, height),
            (width, depth, height),
            (0, depth, height),
        ]
    ]
    faces = [
        [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]
    ]
    rep = ifcopenshell.api.geometry.add_mesh_representation(
        model, context=context, vertices=vertices, faces=faces
    )
    return rep


def assign_representation(model, product, representation):
    ifcopenshell.api.geometry.assign_representation(
        model, product=product, representation=representation
    )


def create_port(
    model,
    context,
    panel,
    name,
    flow_direction,
    x,
    y,
    z,
    visualize=False,
    color_style=None,
):
    port = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcDistributionPort", name=name
    )
    if hasattr(port, "FlowDirection"):
        port.FlowDirection = flow_direction
    ifcopenshell.api.system.assign_port(model, element=panel, port=port)

    if visualize:
        proxy = ifcopenshell.api.root.create_entity(
            model, ifc_class="IfcBuildingElementProxy", name=f"{name}_Physical_Entry"
        )
        proxy.Description = "Assumed Spatial Port"
        ifcopenshell.api.aggregate.assign_object(
            model, products=[proxy], relating_object=panel
        )
        port_size = 0.05
        rep = create_box_representation(model, context, port_size, port_size, port_size)
        ifcopenshell.api.geometry.assign_representation(
            model, product=proxy, representation=rep
        )
        if color_style:
            ifcopenshell.api.style.assign_item_style(
                model, item=rep.Items[0], style=color_style
            )

        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        ifcopenshell.api.geometry.edit_object_placement(
            model, product=proxy, matrix=matrix
        )
    return port


def create_subcomponent(
    model, context, parent_panel, line_data, instance_index, x, y, z, w, d, h, color
):
    """Creates a localized child component attached to the main panel."""
    part_number = line_data.get("part_number", "Unknown")
    category = line_data.get("item_category", "Component")
    ifc_class = IFC_CLASS_MAP.get(category, "IfcDiscreteAccessory")

    # 1. Create Entity
    comp_name = f"{category}_{part_number}_{instance_index}"
    comp = ifcopenshell.api.root.create_entity(
        model, ifc_class=ifc_class, name=comp_name
    )
    comp.Description = line_data.get("description", "")

    # 2. Assign to Parent (Creates IfcRelAggregates hierarchy)
    ifcopenshell.api.aggregate.assign_object(
        model, products=[comp], relating_object=parent_panel
    )

    # 3. Create & Assign Geometry
    rep = create_box_representation(model, context, w, d, h)
    ifcopenshell.api.geometry.assign_representation(
        model, product=comp, representation=rep
    )
    if color:
        ifcopenshell.api.style.assign_item_style(model, item=rep.Items[0], style=color)

    # 4. Position Relative to Panel
    matrix = np.eye(4)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z
    ifcopenshell.api.geometry.edit_object_placement(model, product=comp, matrix=matrix)

    # 5. Assign Metadata
    add_pset(
        model,
        comp,
        "Pset_ManufacturerTypeInformation",
        {
            "Manufacturer": "Schneider Electric",
            "ArticleNumber": part_number,
            "ModelLabel": line_data.get("item", ""),
        },
    )

    return comp


# ------------------------------------------------------------
# Main Execution Logic
# ------------------------------------------------------------
def generate_ifc_from_twin(twin_data: dict, visualize_ports: bool = False) -> bytes:
    data = twin_data

    # Setup Model and Contexts
    model = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcProject", name="Digital Twin BIM Library"
    )
    ifcopenshell.api.unit.assign_unit(model)

    model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )

    # Spatial Structure
    site = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcSite", name="Default Site"
    )
    building = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcBuilding", name="Default Building"
    )
    storey = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcBuildingStorey", name="Default Storey"
    )
    space = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcSpace", name="Plant Room"
    )

    ifcopenshell.api.aggregate.assign_object(
        model, products=[site], relating_object=project
    )
    ifcopenshell.api.aggregate.assign_object(
        model, products=[building], relating_object=site
    )
    ifcopenshell.api.aggregate.assign_object(
        model, products=[storey], relating_object=building
    )
    ifcopenshell.api.aggregate.assign_object(
        model, products=[space], relating_object=storey
    )

    # --- Colors ---
    gray_style = create_color_style(
        model, "Panel_Gray_Glass", 0.6, 0.6, 0.62, transparency=0.7
    )
    warning_red_style = create_color_style(model, "Warning_Red", 0.9, 0.1, 0.1)
    door_clearance_style = create_color_style(
        model, "Clearance_Door", 0.2, 0.5, 0.8, transparency=0.8
    )
    cable_clearance_style = create_color_style(
        model, "Clearance_Cable", 0.9, 0.8, 0.1, transparency=0.8
    )

    # Subcomponent Colors
    door_comp_style = create_color_style(model, "Door_Comp", 0.1, 0.6, 0.2)
    internal_comp_style = create_color_style(model, "Internal_Comp", 0.3, 0.3, 0.3)
    terminal_style = create_color_style(model, "Terminal", 0.8, 0.8, 0.8)

    # Panel Creation
    config_id = data.get("config_id", "Unknown_Panel")
    panel_type = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcElectricDistributionBoardType", name=f"{config_id}_Type"
    )
    panel = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcElectricDistributionBoard", name=config_id
    )

    notes = data.get("notes", "")
    if notes:
        panel.Description = notes

    ifcopenshell.api.type.assign_type(
        model, related_objects=[panel], relating_type=panel_type
    )
    ifcopenshell.api.spatial.assign_container(
        model, products=[panel], relating_structure=space
    )

    matrix = np.eye(4)
    ifcopenshell.api.geometry.edit_object_placement(model, product=panel, matrix=matrix)

    # Panel Geometry
    enclosure = data.get("enclosure", {})
    dim_string = (
        enclosure.get("dimensions_mm", "1000x800x300") if enclosure else "1000x800x300"
    )
    dims = dim_string.lower().split("x")
    h_mm, w_mm, d_mm = 1000.0, 800.0, 300.0
    if len(dims) == 3:
        try:
            h_mm, w_mm, d_mm = float(dims[0]), float(dims[1]), float(dims[2])
        except ValueError:
            pass

    width = mm_to_m(w_mm)
    depth = mm_to_m(d_mm)
    height = mm_to_m(h_mm)

    rep = create_box_representation(model, body_context, width, depth, height)
    assign_representation(model, panel_type, rep)
    ifcopenshell.api.style.assign_item_style(model, item=rep.Items[0], style=gray_style)

    # Identity Data
    core_part = next(
        (
            c.get("part_number", "")
            for c in data.get("components", [])
            if c.get("item_category") == "Core Device"
        ),
        "",
    )
    derived_url = f"https://www.se.com/ww/en/product/{core_part}/" if core_part else ""

    add_pset(
        model,
        panel_type,
        "Pset_ManufacturerTypeInformation",
        {
            "Manufacturer": "Schneider Electric",
            "ModelLabel": data.get("config_id", ""),
            "ModelReference": data.get("series_id", ""),
            "ArticleNumber": data.get("enclosure", {}).get("catalog_ref", ""),
            "Description": data.get("notes", ""),
            "ManufacturerUrl": derived_url,
        },
    )

    add_pset(
        model,
        panel_type,
        "DT_Pset_Electrical",
        {
            "MotorPower_kW": float(data.get("motor_power_kw", 0)),
            "LoadCount": int(data.get("load_count", 0)),
            "CommunicationProtocol": data.get("communication", ""),
        },
    )

    # ------------------------------------------------------------
    # Hierarchical Component Generation (LOD 350 Sub-components)
    # ------------------------------------------------------------
    bom_lines = data.get("bom_lines", [])

    # Adaptive Cursors
    z_cursor_backplate = height - 0.15
    z_cursor_door = height - 0.10
    x_cursor_terminals = 0.05

    for line in bom_lines:
        cat = line.get("item_category", "")
        if cat == "Enclosure":
            continue

        qty = int(float(line.get("qty", "1")))

        # Calculate dynamic horizontal spacing blocks
        x_spacing = width / (qty + 1)

        for i in range(qty):
            if "PB" in cat or "Pilot Light" in cat:
                # Mount on Door (y = depth)
                cw, cd, ch = 0.03, 0.015, 0.03
                cx = (x_spacing * (i + 1)) - (cw / 2)
                cy = depth - cd  # Embedded slightly into the door
                cz = z_cursor_door
                color = door_comp_style

            elif "Terminal" in cat:
                # Mount on bottom DIN rail (left to right)
                cw, cd, ch = 0.006, 0.05, 0.05
                cx = x_cursor_terminals
                cy = 0.05
                cz = 0.1
                x_cursor_terminals += 0.007
                color = terminal_style

            elif "Gland" in cat:
                # Mount on Bottom Gland Plate (z = 0)
                cw, cd, ch = 0.04, 0.04, 0.04
                cx = (x_spacing * (i + 1)) - (cw / 2)
                cy = (depth / 2) - (cd / 2)  # Centered on bottom depth
                cz = -ch / 2  # Protruding down from bottom face
                color = terminal_style

            else:
                # Mount on Backplate Motor Branches (y = 0.05)
                cw, cd, ch = 0.06, 0.1, 0.1
                cx = (x_spacing * (i + 1)) - (cw / 2)
                cy = 0.02
                cz = z_cursor_backplate
                color = internal_comp_style

            create_subcomponent(
                model=model,
                context=body_context,
                parent_panel=panel,
                line_data=line,
                instance_index=i + 1,
                x=cx,
                y=cy,
                z=cz,
                w=cw,
                d=cd,
                h=ch,
                color=color,
            )

        # Update height cursors when the row is finished so the next components stack below
        if "PB" in cat or "Pilot Light" in cat:
            z_cursor_door -= 0.08
        elif "Terminal" not in cat and "Gland" not in cat:
            z_cursor_backplate -= 0.15

    # Ports
    create_port(
        model,
        body_context,
        panel,
        "Incoming_Power",
        "SINK",
        x=width * 0.2,
        y=depth * 0.5,
        z=height,
        visualize=visualize_ports,
        color_style=warning_red_style,
    )
    load_count = int(data.get("load_count", 0))
    for i in range(1, load_count + 1):
        create_port(
            model,
            body_context,
            panel,
            f"Motor_{i}_Outgoing",
            "SOURCE",
            x=width * (i / (load_count + 1)),
            y=depth * 0.5,
            z=0.0,
            visualize=visualize_ports,
            color_style=warning_red_style,
        )

    comm_protocol = data.get("communication")
    if comm_protocol and comm_protocol.lower() != "none":
        create_port(
            model,
            body_context,
            panel,
            f"Comm_{comm_protocol}",
            "SOURCEANDSINK",
            x=width * 0.8,
            y=depth * 0.5,
            z=height,
            visualize=visualize_ports,
            color_style=warning_red_style,
        )

    # Clearances
    if visualize_ports:
        create_clearance_zone(
            model,
            body_context,
            panel,
            "Clearance_WorkingSpace",
            width=width,
            depth=1.0,
            height=max(height, 2.0),
            x=0,
            y=depth,
            z=0,
            color_style=door_clearance_style,
        )
        create_clearance_zone(
            model,
            body_context,
            panel,
            "Clearance_TopCables",
            width=width,
            depth=depth,
            height=0.4,
            x=0,
            y=0,
            z=height,
            color_style=cable_clearance_style,
        )

    return model.to_string().encode("utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Generate an IFC BIM object from a Digital Twin JSON."
    )
    parser.add_argument(
        "--visualize-ports", action="store_true", help="Generate physical 3D boxes."
    )
    parser.add_argument(
        "-o", "--output-name", type=str, help="Base name for the output IFC file."
    )
    args = parser.parse_args()

    # Load Data (Defaults to the uploaded JSON name if the other is not found)
    json_path = "002_DigitalTwin_DNA_CFG-SS011-2X.json"
    try:
        data = load_data(json_path)
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return

    content = generate_ifc_from_twin(data, visualize_ports=args.visualize_ports)

    config_id = data.get("config_id", "Unknown_Panel")
    base_name = args.output_name if args.output_name else config_id
    suffix = "_Visual" if args.visualize_ports else "_Logical"
    output_path = f"{base_name}{suffix}.ifc"

    with open(output_path, "wb") as f:
        f.write(content)
    print(f"Successfully wrote: {output_path}")


if __name__ == "__main__":
    main()
