import json
import argparse
import numpy as np
import ifcopenshell
import ifcopenshell.api

# Explicit API imports (required in 0.8+)
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

def load_data(path="DigitalTwin_DNA_CFG-ST019-3X.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def add_pset(model, product, name, properties):
    clean_properties = {k: v for k, v in properties.items() if v is not None}
    pset = ifcopenshell.api.pset.add_pset(model, product=product, name=name)
    ifcopenshell.api.pset.edit_pset(model, pset=pset, properties=clean_properties)
    return pset

def create_box_representation(model, context, width, depth, height):
    vertices = [[
        (0, 0, 0), (width, 0, 0), (width, depth, 0), (0, depth, 0),
        (0, 0, height), (width, 0, height), (width, depth, height), (0, depth, height)
    ]]
    faces = [[
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)
    ]]
    rep = ifcopenshell.api.geometry.add_mesh_representation(
        model, context=context, vertices=vertices, faces=faces
    )
    return rep

def assign_representation(model, product, representation):
    ifcopenshell.api.geometry.assign_representation(
        model, product=product, representation=representation
    )

def create_color_style(model, name, r, g, b):
    """
    Creates an IFC Surface Style with specific RGB values (0.0 to 1.0).
    """
    style = ifcopenshell.api.style.add_style(model, name=name)
    ifcopenshell.api.style.add_surface_style(
        model, 
        style=style, 
        ifc_class="IfcSurfaceStyleRendering", 
        attributes={
            "SurfaceColour": {"Name": None, "Red": float(r), "Green": float(g), "Blue": float(b)}
        }
    )
    return style

def create_port(model, context, panel, name, flow_direction, x, y, z, visualize=False, color_style=None):
    """
    Creates a logical IfcDistributionPort. If visualize=True, also creates
    an IfcBuildingElementProxy with a 3D box to represent the port spatially.
    """
    # 1. THE LOGICAL DATA
    port = ifcopenshell.api.root.create_entity(
        model, ifc_class="IfcDistributionPort", name=name
    )

    if hasattr(port, "FlowDirection"):
        port.FlowDirection = flow_direction

    ifcopenshell.api.system.assign_port(
        model, element=panel, port=port
    )

    # 2. THE PHYSICAL VISUALIZATION
    if visualize:
        proxy = ifcopenshell.api.root.create_entity(
            model,
            ifc_class="IfcBuildingElementProxy",
            name=f"{name}_Physical_Entry"
        )
        proxy.Description = "WARNING: Spatial location is strictly an assumption for visual prototyping. Not validated by the Digital Twin single source of truth."

        ifcopenshell.api.aggregate.assign_object(
            model, products=[proxy], relating_object=panel
        )

        port_size = 0.05 
        rep = create_box_representation(
            model, context, port_size, port_size, port_size
        )
        ifcopenshell.api.geometry.assign_representation(
            model, product=proxy, representation=rep
        )

        # Apply the warning color to the geometry mesh (Items[0])
        if color_style:
            ifcopenshell.api.style.assign_item_style(model, item=rep.Items[0], style=color_style)

        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        ifcopenshell.api.geometry.edit_object_placement(
            model, product=proxy, matrix=matrix
        )

    return port

# ------------------------------------------------------------
# Main Execution Logic
# ------------------------------------------------------------
def generate_ifc_from_twin(twin_data: dict, visualize_ports: bool = False) -> bytes:
    """
    Generates an IFC (BIM) object from digital twin data.
    Returns the IFC file content as bytes.
    """
    data = twin_data

    # Setup Model and Contexts
    model = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Digital Twin BIM Library")
    ifcopenshell.api.unit.assign_unit(model)

    model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body_context = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body",
        target_view="MODEL_VIEW", parent=model_context
    )

    # Spatial Structure
    site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="Default Site")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Default Building")
    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Default Storey")
    space = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSpace", name="Plant Room")

    ifcopenshell.api.aggregate.assign_object(model, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(model, products=[storey], relating_object=building)
    ifcopenshell.api.aggregate.assign_object(model, products=[space], relating_object=storey)

    # ---  Create our Color Styles ---
    gray_style = create_color_style(model, "Panel_Gray", 0.6, 0.6, 0.62)
    warning_red_style = create_color_style(model, "Warning_Red", 0.9, 0.1, 0.1)

    # Panel Creation
    config_id = data.get("config_id", "Unknown_Panel")
    panel_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcElectricDistributionBoardType", name=f"{config_id}_Type")
    panel = ifcopenshell.api.root.create_entity(model, ifc_class="IfcElectricDistributionBoard", name=config_id)
    
    notes = data.get("notes", "")
    if notes:
        panel.Description = notes

    ifcopenshell.api.type.assign_type(model, related_objects=[panel], relating_type=panel_type)
    ifcopenshell.api.spatial.assign_container(model, products=[panel], relating_structure=space)
    
    matrix = np.eye(4)
    ifcopenshell.api.geometry.edit_object_placement(model, product=panel, matrix=matrix)

    # Panel Geometry
    enclosure = data.get("enclosure", {})
    dim_string = enclosure.get("dimensions_mm", "1000x800x300") if enclosure else "1000x800x300"
    dims = dim_string.lower().split('x')
    h_mm, w_mm, d_mm = 1000, 800, 300 
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
    
    # --- Apply the Gray color to the Panel's geometry mesh ---
    ifcopenshell.api.style.assign_item_style(model, item=rep.Items[0], style=gray_style)

    # Psets
    add_pset(model, panel_type, "DT_Pset_Identity", {
        "ConfigID": data.get("config_id", ""),
        "SeriesID": data.get("series_id", "")
    })
    add_pset(model, panel_type, "DT_Pset_Electrical", {
        "MotorPower_kW": float(data.get("motor_power_kw", 0)),
        "LoadCount": int(data.get("load_count", 0)),
        "CommunicationProtocol": data.get("communication", "")
    })

    # Ports
    create_port(
        model, body_context, panel, "Incoming_Power", "SINK", 
        x=width * 0.2, y=depth * 0.5, z=height, 
        visualize=visualize_ports, color_style=warning_red_style
    )

    load_count = int(data.get("load_count", 0))
    for i in range(1, load_count + 1):
        x_pos = width * (i / (load_count + 1))
        create_port(
            model, body_context, panel, f"Motor_{i}_Outgoing", "SOURCE", 
            x=x_pos, y=depth * 0.5, z=0.0, 
            visualize=visualize_ports, color_style=warning_red_style
        )

    comm_protocol = data.get("communication")
    if comm_protocol and comm_protocol.lower() != "none":
        create_port(
            model, body_context, panel, f"Comm_{comm_protocol}", "SOURCEANDSINK", 
            x=width * 0.8, y=depth * 0.5, z=height, 
            visualize=visualize_ports, color_style=warning_red_style
        )

    return model.to_string().encode("utf-8")

def main():
    parser = argparse.ArgumentParser(description="Generate an IFC BIM object from a Digital Twin JSON.")
    parser.add_argument("--visualize-ports", action="store_true", help="Generate physical 3D boxes.")
    parser.add_argument("-o", "--output-name", type=str, help="Base name for the output IFC file.")
    args = parser.parse_args()

    # Load Data
    json_path = "DigitalTwin_DNA_CFG-ST019-3X.json"
    try:
        data = load_data(json_path)
    except FileNotFoundError:
        print(f"Error: {json_path} not found for testing.")
        return

    content = generate_ifc_from_twin(data, visualize_ports=args.visualize_ports)

    # Save
    config_id = data.get("config_id", "Unknown_Panel")
    base_name = args.output_name if args.output_name else config_id
    suffix = "_Visual" if args.visualize_ports else "_Logical"
    output_path = f"{base_name}{suffix}.ifc"
    
    with open(output_path, "wb") as f:
        f.write(content)
    print(f"Successfully wrote: {output_path}")

if __name__ == "__main__":
    main()
