import io
import json
import zipfile
from datetime import datetime, timezone
from ..schemas.configurator import DigitalTwinResponse
from ..generators.excel_gen import generate_excel_from_twin
from ..generators.word_gen import generate_word_from_twin

class ZipService:
    @staticmethod
    def create_project_package(twin: DigitalTwinResponse) -> bytes:
        """
        Orchestrates the generation of Excel, Word, JSON and packages
        them all into a single structured ZIP file in memory.
        """
        assets = [a.strip() for a in (twin.selected_assets or [])]
        
        # 1. Determine which engine generators to fire
        # Match case-insensitively just to be robust
        def has_asset(name):
            return any(a.lower() == name.lower() for a in assets)

        gen_excel = has_asset("Data Sheet") or has_asset("Bill of Materials")
        gen_word = has_asset("Specification")
        
        excel_bytes = generate_excel_from_twin(twin) if gen_excel else None
        word_bytes = generate_word_from_twin(twin) if gen_word else None
        
        # 2. Build the Manifest dynamically
        files_included = [f"Neutral/DigitalTwin_DNA_{twin.config_id}.json"]
        if excel_bytes: files_included.append(f"Neutral/ApplicationPack_{twin.config_id}.xlsx")
        if word_bytes: files_included.append(f"Docs/EngineeringSpec_{twin.config_id}.docx")
        
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
            zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))
            # Always output Neural JSON DNA
            zip_file.writestr(f"Neutral/DigitalTwin_DNA_{twin.config_id}.json", twin.model_dump_json(indent=2))
            
            # Conditionally write generated files
            if excel_bytes:
                zip_file.writestr(f"Neutral/ApplicationPack_{twin.config_id}.xlsx", excel_bytes)
            if word_bytes:
                zip_file.writestr(f"Docs/EngineeringSpec_{twin.config_id}.docx", word_bytes)
            
        zip_buffer.seek(0)
        return zip_buffer.read()
