import io
import json
import zipfile
from datetime import datetime, timezone
from ..schemas.configurator import DigitalTwinResponse
from ..generators.excel_gen import generate_excel_from_twin
from ..generators.word_gen import generate_word_from_twin
from ..generators.bim_gen import generate_ifc_from_twin
from ..generators.templates.readme_template import generate_readme_from_twin
from ..generators.spec_text_gen import generate_spec_text_from_twin

class ZipService:
    @staticmethod
    def create_project_package(twin: DigitalTwinResponse) -> bytes:
        """
        Orchestrates the generation of Excel, Word, IFC, JSON and packages
        them all into a single structured ZIP file in memory.
        """
        assets = [a.strip() for a in (twin.selected_assets or [])]
        
        # 1. Determine which engine generators to fire
        # Match case-insensitively just to be robust
        def has_asset(name):
            return any(a.lower() == name.lower() for a in assets)

        gen_excel = has_asset("Data Sheet") or has_asset("Bill of Materials")
        gen_word = has_asset("Specification")
        gen_bim = has_asset("BIM Object")
        
        excel_files = generate_excel_from_twin(twin) if gen_excel else {}
        word_bytes = generate_word_from_twin(twin) if gen_word else None
        
        # BIM objects (Logical and Visual)
        # Convert twin to dict for bim_gen
        twin_dict = twin.model_dump()
        bim_logical = generate_ifc_from_twin(twin_dict, visualize_ports=False) if gen_bim else None
        bim_visual = generate_ifc_from_twin(twin_dict, visualize_ports=True) if gen_bim else None
        
        readme_bytes = generate_readme_from_twin(twin)
        spec_text_bytes = generate_spec_text_from_twin(twin)
        
        # 2. Build the Manifest dynamically
        files_included = [f"002_DigitalTwin_DNA_{twin.config_id}.json", "003_README.txt", "014_SpecTextBlock.txt"]
        if excel_files: 
            files_included.extend(list(excel_files.keys()))
        if word_bytes: files_included.append(f"004_EngineeringSpec_{twin.config_id}.docx")
        if bim_logical: files_included.append(f"BIM/015_Logical_{twin.config_id}.ifc")
        if bim_visual: files_included.append(f"BIM/016_Visual_{twin.config_id}.ifc")
        
        manifest = {
            "config_id": twin.config_id,
            "series": twin.series_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files_included": files_included
        }
        
        # 3. Create the ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # Root manifest
            zip_file.writestr("001_manifest.json", json.dumps(manifest, indent=2))
            zip_file.writestr("003_README.txt", readme_bytes)
            zip_file.writestr("014_SpecTextBlock.txt", spec_text_bytes)
            # Always output Neural JSON DNA
            zip_file.writestr(f"002_DigitalTwin_DNA_{twin.config_id}.json", twin.model_dump_json(indent=2))
            
            # Conditionally write generated files
            for filename, filebytes in excel_files.items():
                zip_file.writestr(filename, filebytes)
                
            if word_bytes:
                zip_file.writestr(f"004_EngineeringSpec_{twin.config_id}.docx", word_bytes)
            if bim_logical:
                zip_file.writestr(f"BIM/015_Logical_{twin.config_id}.ifc", bim_logical)
            if bim_visual:
                zip_file.writestr(f"BIM/016_Visual_{twin.config_id}.ifc", bim_visual)
            
        zip_buffer.seek(0)
        return zip_buffer.read()
