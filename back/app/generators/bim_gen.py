import json
import argparse
import numpy as np
import traceback
import sys
import ifcopenshell
import ifcopenshell.api

# Explicit API imports
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.pset
import ifcopenshell.api.geometry
import ifcopenshell.api.system
import ifcopenshell.api.style

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def mm_to_m(v_mm):
    return v_mm / 1000.0


def load_data(path="002_DigitalTwin_DNA_CFG-V019-4X.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_pset(model, product, name, properties):
    clean_properties = {k: v for k, v in properties.items() if v is not None}
    pset = ifcopenshell.api.pset.add_pset(model, product=product, name=name)
    ifcopenshell.api.pset.edit_pset(model, pset=pset, properties=clean_properties)
    return pset


def create_color_style(model, name, r, g, b, transparency=0.0):
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


def create_multi_bay_enclosure(model, context, bay_width, depth, height, count):
    vertices = []
    faces = []

    for i in range(count):
        x0 = i * bay_width
        x1 = (i + 1) * bay_width

        bay_vertices = [
            (x0, 0, 0),
            (x1, 0, 0),
            (x1, depth, 0),
            (x0, depth, 0),
            (x0, 0, height),
            (x1, 0, height),
            (x1, depth, height),
            (x0, depth, height),
        ]

        bay_faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]

        vertices.append(bay_vertices)
        faces.append(bay_faces)

    rep = ifcopenshell.api.geometry.add_mesh_representation(
        model, context=context, vertices=vertices, faces=faces
    )
    return rep


def create_box_representation(model, context, width, depth, height):
    return create_multi_bay_enclosure(model, context, width, depth, height, 1)


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
        proxy.Description = "WARNING: Spatial location is strictly an assumption for visual prototyping."
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
        matrix[0, 3], matrix[1, 3], matrix[2, 3] = x, y, z
        ifcopenshell.api.geometry.edit_object_placement(
            model, product=proxy, matrix=matrix
        )

    return port


def create_clearance_zone(
    model, context, panel, name, width, depth, height, x, y, z, color_style
):
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
    matrix[0, 3], matrix[1, 3], matrix[2, 3] = x, y, z
    ifcopenshell.api.geometry.edit_object_placement(model, product=proxy, matrix=matrix)


def create_door_button(model, context, panel, name, x, y, z, color_style):
    button = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcDiscreteAccessory", name=name
    )
    ifcopenshell.api.aggregate.assign_object(
        model, products=[button], relating_object=panel
    )

    s, d = 0.03, 0.01
    rep = create_box_representation(model, context, s, d, s)
    ifcopenshell.api.geometry.assign_representation(
        model, product=button, representation=rep
    )
    if color_style:
        ifcopenshell.api.style.assign_item_style(
            model, item=rep.Items[0], style=color_style
        )

    matrix = np.eye(4)
    matrix[0, 3] = x - (s / 2)
    matrix[1, 3] = y
    matrix[2, 3] = z - (s / 2)
    ifcopenshell.api.geometry.edit_object_placement(
        model, product=button, matrix=matrix
    )


# ------------------------------------------------------------
# Main Execution Logic
# ------------------------------------------------------------
def generate_ifc_from_twin(twin_data: dict, visualize_ports: bool = False) -> bytes:
    try:
        data = twin_data
        model = ifcopenshell.api.project.create_file(version="IFC4")
        project = ifcopenshell.api.root.create_entity(
            model, ifc_class="IfcProject", name="Digital Twin BIM Library"
        )
        ifcopenshell.api.unit.assign_unit(model)

        model_context = ifcopenshell.api.context.add_context(
            model, context_type="Model"
        )
        body_context = ifcopenshell.api.context.add_context(
            model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_context,
        )

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

        gray_style = create_color_style(model, "Panel_Gray", 0.6, 0.6, 0.62)
        warning_red_style = create_color_style(model, "Warning_Red", 0.9, 0.1, 0.1)
        status_green_style = create_color_style(model, "Status_Green", 0.1, 0.8, 0.2)
        door_clearance_style = create_color_style(
            model, "Clearance_Door", 0.2, 0.5, 0.8, transparency=0.85
        )

        config_id = data.get("config_id", "Unknown_Panel")
        panel_type = ifcopenshell.api.root.create_entity(
            model,
            ifc_class="IfcElectricDistributionBoardType",
            name=f"{config_id}_Type",
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
        ifcopenshell.api.geometry.edit_object_placement(
            model, product=panel, matrix=matrix
        )

        enclosure = data.get("enclosure", {})
        dim_string = (
            enclosure.get("dimensions_mm", "1000x800x300")
            if enclosure
            else "1000x800x300"
        )
        dims = dim_string.lower().split("x")
        h_mm, w_mm, d_mm = 1000, 800, 300
        if len(dims) == 3:
            try:
                h_mm, w_mm, d_mm = float(dims[0]), float(dims[1]), float(dims[2])
            except ValueError:
                pass

        enclosure_count = int(data.get("enclosure_count", 1))
        bay_width = mm_to_m(w_mm)
        depth = mm_to_m(d_mm)
        height = mm_to_m(h_mm)
        total_width = bay_width * enclosure_count

        rep = create_multi_bay_enclosure(
            model, body_context, bay_width, depth, height, enclosure_count
        )
        assign_representation(model, panel_type, rep)
        ifcopenshell.api.style.assign_item_style(
            model, item=rep.Items[0], style=gray_style
        )

        components = data.get("components", [])
        core_part = next(
            (
                c.get("part_number", "")
                for c in components
                if c.get("item_category") == "Core Device"
            ),
            "",
        )
        derived_url = (
            f"https://www.se.com/ww/en/product/{core_part}/" if core_part else ""
        )

        add_pset(
            model,
            panel_type,
            "Pset_ManufacturerTypeInformation",
            {
                "Manufacturer": "Schneider Electric",
                "ModelLabel": data.get("config_id", ""),
                "ModelReference": data.get("series_id", ""),
                "ArticleNumber": enclosure.get("catalog_ref", ""),
                "Description": data.get("series_name", "Control Panel"),
                "ManufacturerUrl": derived_url,
            },
        )

        add_pset(
            model,
            panel_type,
            "Pset_ElectricalDeviceCommon",
            {
                "IP_Code": enclosure.get("ip_rating", "IP20"),
                "IK_Code": enclosure.get("ik_rating", "IK08"),
            },
        )

        add_pset(
            model,
            panel_type,
            "DT_Pset_Identity",
            {
                "ConfigID": data.get("config_id", ""),
                "SeriesID": data.get("series_id", ""),
                "EnclosureMaterial": enclosure.get("material", ""),
                "DoorType": enclosure.get("door_type", ""),
                "EnclosureCount": enclosure_count,
            },
        )

        add_pset(
            model,
            panel_type,
            "DT_Pset_Electrical",
            {
                "MotorPower_kW": float(data.get("motor_power_kw", 0)),
                "LoadCount": int(data.get("load_count", 0)),
                "CommunicationProtocol": data.get("communication", "None"),
            },
        )

        components_str = " | ".join(
            [
                f"{c.get('qty','1')}x {c.get('part_number','')} ({c.get('item_category','')})"
                for c in components
            ]
        )
        accessories_str = " | ".join(
            [
                f"{a.get('qty','1')}x {a.get('part_number','')} ({a.get('category','')})"
                for a in data.get("accessories", [])
            ]
        )

        add_pset(
            model,
            panel_type,
            "DT_Pset_BillOfMaterials",
            {
                "InternalComponents": (
                    components_str if components_str else "None defined"
                ),
                "Accessories": accessories_str if accessories_str else "None defined",
            },
        )

        create_port(
            model,
            body_context,
            panel,
            "Incoming_Power",
            "SINK",
            x=total_width * 0.2,
            y=depth * 0.5,
            z=height,
            visualize=visualize_ports,
            color_style=warning_red_style,
        )

        load_count = int(data.get("load_count", 0))
        for i in range(1, load_count + 1):
            x_pos = total_width * (i / (load_count + 1))
            create_port(
                model,
                body_context,
                panel,
                f"Motor_{i}_Outgoing",
                "SOURCE",
                x=x_pos,
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
                x=total_width * 0.8,
                y=depth * 0.5,
                z=height,
                visualize=visualize_ports,
                color_style=warning_red_style,
            )

        if visualize_ports and load_count > 0:
            # FIX 1: Dynamically calculate top Z-coordinate to prevent floating buttons on smaller panels.
            # Caps at 1.6m ergonomic height, or adjusts downwards based on panel height.
            top_btn_z = min(1.60, height - 0.1)

            for i in range(1, load_count + 1):
                btn_x = total_width * (i / (load_count + 1))
                create_door_button(
                    model,
                    body_context,
                    panel,
                    f"Trip_Light_{i}",
                    btn_x,
                    depth,
                    top_btn_z,
                    warning_red_style,
                )
                create_door_button(
                    model,
                    body_context,
                    panel,
                    f"Run_Light_{i}",
                    btn_x,
                    depth,
                    top_btn_z - 0.05,
                    status_green_style,
                )
                create_door_button(
                    model,
                    body_context,
                    panel,
                    f"Stop_PB_{i}",
                    btn_x,
                    depth,
                    top_btn_z - 0.15,
                    warning_red_style,
                )
                create_door_button(
                    model,
                    body_context,
                    panel,
                    f"Start_PB_{i}",
                    btn_x,
                    depth,
                    top_btn_z - 0.20,
                    status_green_style,
                )

        if visualize_ports:
            # FIX 2: Dynamic working depth for visual aesthetics on smaller panels.
            working_depth = max(0.6, min(1.0, depth * 2.5))

            create_clearance_zone(
                model,
                body_context,
                panel,
                "Clearance_WorkingSpace",
                width=total_width,
                depth=working_depth,
                height=height,
                x=0,
                y=depth,
                z=0,
                color_style=door_clearance_style,
            )

        return model.to_string().encode("utf-8")

    except Exception:
        print("\n[CRITICAL ERROR] The IFC generation failed during execution:")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)


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

    json_path = "002_DigitalTwin_DNA_CFG-V014-3X.json"
    try:
        data = load_data(json_path)
    except FileNotFoundError:
        print(
            f"[ERROR] {json_path} not found. Ensure the file is in the same directory."
        )
        return
    except json.JSONDecodeError as e:
        print(
            f"[ERROR] Failed to parse JSON file. Ensure it is valid JSON. Details: {e}"
        )
        return

    content = generate_ifc_from_twin(data, visualize_ports=args.visualize_ports)

    if content is None:
        print(
            "[ERROR] generate_ifc_from_twin returned None. Check the critical error traceback above."
        )
        return

    config_id = data.get("config_id", "Unknown_Panel")
    base_name = args.output_name if args.output_name else config_id
    suffix = "_Visual" if args.visualize_ports else "_Logical"
    output_path = f"{base_name}{suffix}.ifc"

    try:
        with open(output_path, "wb") as f:
            f.write(content)
        print(f"\n[SUCCESS] Successfully wrote: {output_path}")
    except IOError as e:
        print(f"[ERROR] Failed to write the IFC file to disk: {e}")


if __name__ == "__main__":
    main()
