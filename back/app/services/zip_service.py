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
        # Generate raw files in memory natively
        excel_bytes = generate_excel_from_twin(twin)
        word_bytes = generate_word_from_twin(twin)
        
        # Create manifest
        manifest = {
            "config_id": twin.config_id,
            "series": twin.series_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "files_included": [
                f"Neutral/DigitalTwin_DNA_{twin.config_id}.json",
                f"Neutral/ApplicationPack_{twin.config_id}.xlsx",
                f"Docs/EngineeringSpec_{twin.config_id}.docx"
            ]
        }
        
        # Create the ZIP archive entirely in memory using BytesIO
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # 1. Write the Manifest to root
            zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # 2. Write Neutral JSON
            zip_file.writestr(
                f"Neutral/DigitalTwin_DNA_{twin.config_id}.json", 
                twin.model_dump_json(indent=2)
            )
            
            # 3. Write Neutral Excel
            zip_file.writestr(
                f"Neutral/ApplicationPack_{twin.config_id}.xlsx", 
                excel_bytes
            )
            
            # 4. Write Docs Word
            zip_file.writestr(
                f"Docs/EngineeringSpec_{twin.config_id}.docx", 
                word_bytes
            )
            
        zip_buffer.seek(0)
        return zip_buffer.read()
