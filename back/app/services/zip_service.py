import io
import json
import zipfile
from datetime import datetime, timezone

from ..generators.asset_number_gen import generate_asset_numbers
from ..generators.bim_gen import generate_ifc_from_twin
from ..generators.excel_gen import generate_excel_from_twin
from ..generators.spec_text_gen import generate_spec_text_from_twin
from ..generators.templates.readme_template import generate_readme_from_twin
from ..generators.word_gen import generate_word_from_twin
from ..schemas.configurator import DigitalTwinResponse
from ..utils.assets import flatten_asset_ids
from .storage_service import StorageService
from botocore.exceptions import ClientError


class ZipService:
    def __init__(self):
        self.storage_service = StorageService()

    def create_project_package(self, twin: DigitalTwinResponse) -> bytes:
        """
        Orchestrates the generation of Excel, Word, IFC, JSON and packages
        them all into a single structured ZIP file in memory.
        """
        assets = flatten_asset_ids(twin.selected_assets)
        asset_numbers = generate_asset_numbers(assets)  # dict of dynamic asset numbers

        # 1. Determine which engine generators to fire
        def has_asset(name):
            return any(a.lower() == name.lower() for a in assets)

        gen_excel = has_asset("Data Sheet")
        gen_word = has_asset("Specification")
        gen_bim = has_asset("BIM Object")
        gen_diagram = has_asset("Multi Line Diagram")
        gen_drawings = has_asset("Drawings")

        excel_files = generate_excel_from_twin(twin) if gen_excel else {}
        word_bytes = generate_word_from_twin(twin) if gen_word else None

        twin_dict = twin.model_dump()
        bim_logical = (
            generate_ifc_from_twin(twin_dict, visualize_ports=False)
            if gen_bim
            else None
        )
        bim_visual = (
            generate_ifc_from_twin(twin_dict, visualize_ports=True) if gen_bim else None
        )

        readme_bytes = generate_readme_from_twin(twin)
        spec_text_bytes = (
            generate_spec_text_from_twin(twin) if has_asset("Specification") else None
        )

        # 2. Build the Manifest dynamically
        files_included = [
            f"002_DigitalTwin_DNA_{twin.config_id}.json",
            "003_README.txt",
        ]
        if excel_files:
            files_included.extend(list(excel_files.keys()))
        if gen_diagram:
            files_included.append(f"{asset_numbers['MLD-svg']}_MultiLineDiagram.svg")
            files_included.append(f"{asset_numbers['MLD-png']}_MultiLineDiagram.png")
            files_included.append(
                f"{asset_numbers['RefArch']}_ReferenceArchitecture.pdf"
            )
        if word_bytes:
            files_included.append(
                f"{asset_numbers['spec-docx']}_EngineeringSpec_{twin.config_id}.docx"
            )
            files_included.append(f"{asset_numbers['spec-txt']}_SpecTextBlock.txt")
        if bim_logical:
            files_included.append(
                f"BIM/{asset_numbers['BIM-logical']}_Logical_{twin.config_id}.ifc"
            )
        if bim_visual:
            files_included.append(
                f"BIM/{asset_numbers['BIM-visual']}_Visual_{twin.config_id}.ifc"
            )
        if gen_drawings:
            files_included.append("Drawings/")

        manifest = {
            "config_id": twin.config_id,
            "series": twin.series_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files_included": files_included,
        }

        # 3. Create the ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Root manifest
            zip_file.writestr("001_manifest.json", json.dumps(manifest, indent=2))
            zip_file.writestr(
                f"002_DigitalTwin_DNA_{twin.config_id}.json",
                twin.model_dump_json(indent=2),
            )
            zip_file.writestr("003_README.txt", readme_bytes)

            # Conditionally write generated files
            for filename, filebytes in excel_files.items():
                zip_file.writestr(filename, filebytes)
            if spec_text_bytes:
                zip_file.writestr(
                    f"{asset_numbers['spec-txt']}_SpecTextBlock.txt", spec_text_bytes
                )
            if word_bytes:
                zip_file.writestr(
                    f"{asset_numbers['spec-docx']}_EngineeringSpec_{twin.config_id}.docx",
                    word_bytes,
                )
            if bim_logical:
                zip_file.writestr(
                    f"BIM/{asset_numbers['BIM-logical']}_Logical_{twin.config_id}.ifc",
                    bim_logical,
                )
            if bim_visual:
                zip_file.writestr(
                    f"BIM/{asset_numbers['BIM-visual']}_Visual_{twin.config_id}.ifc",
                    bim_visual,
                )

            # Drawings logic: write directly to root ZIP
            if gen_drawings:
                folders = ["top", "right", "left", "bottom", "front", "back", "iso"]
                for line in twin.bom_lines:
                    # Filter for components only
                    if line.item_category.lower() in [
                        "soft starter",
                        "magnetic cb",
                        "line contactor",
                        "overload",
                        "variable speed drive",
                    ]:
                        for folder in folders:
                            # S3 key convention: folder/partnumber_folder.dxf
                            s3_key = f"{folder}/{line.part_number.lower()}_{folder}.dxf"
                            try:
                                file_bytes = self.storage_service.get_file(s3_key)
                                zip_file.writestr(
                                    f"Drawings/{folder}/{line.part_number.lower()}_{folder}.dxf",
                                    file_bytes,
                                )
                            except ClientError:
                                continue

        zip_buffer.seek(0)
        return zip_buffer.read()
