from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from ..database import get_db
from ..schemas.configurator import DigitalTwinRequest, DigitalTwinResponse
from ..services.rule_resolver import ConfigurationEngine
from ..services.zip_service import ZipService

router = APIRouter(
    prefix="/api/v1/engine",
    tags=["Core Configuration Engine"],
)

@router.post("/configure", response_model=DigitalTwinResponse)
def generate_digital_twin(request: DigitalTwinRequest, db: Session = Depends(get_db)):
    """
    Main entry point for generating a Digital Twin from high-level specs.
    Expects input like:
    {
      "series_id": "DOL",
      "motor_power_kw": 30,
      "load_count": 2,
      "ats_included": false,
      "control_mode": "Local",
      "ip_rating": "IP54"
    }
    """
    engine = ConfigurationEngine(db)
    
    try:
        twin = engine.generate_twin(request)
        return twin
    except HTTPException as he:
        # Re-raise explicit handled errors
        raise he
    except Exception as e:
         print(f"Error executing engine: {e}")
         raise HTTPException(status_code=500, detail="Internal server error resolving rules")

@router.post("/generate-package")
def generate_asset_package(request: DigitalTwinRequest, db: Session = Depends(get_db)):
    """
    Executes the Digital Twin engineering resolution and automatically bundles
    the resulting models, excel, and word documents into a standard Asset Pack ZIP file.
    """
    engine = ConfigurationEngine(db)
    
    try:
        # 1. Resolve Twin
        twin = engine.generate_twin(request)
        
        # 2. Package Twin into Zip bytes
        zip_bytes = ZipService.create_project_package(twin)
        
        # 3. Stream back as downloadable Zip
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename=ApplicationPack_{twin.config_id}.zip"}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
         print(f"Error packaging project: {e}")
         raise HTTPException(status_code=500, detail="Internal server error assembling zip package")
