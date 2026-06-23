from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app import models


def extract_enclosure_range(enclosure_ref: str) -> str:
    if "CRN" in enclosure_ref.upper():
        return "CRN"
    elif "SM" in enclosure_ref.upper():
        return "SM"
    elif "PLM" in enclosure_ref.upper():
        return "PLM"
    elif "PLA" in enclosure_ref.upper():
        return "PLA"
    elif "SFN" in enclosure_ref.upper():
        return "SFN"
    elif "S3D" in enclosure_ref.upper():
        return "S3D"
    else:
        return "CRN"


def get_motor_start_text(
    db: Session,
    pump_count: int,
    motor_start: str,
    motor_power: float,
    enclosure_ref: str,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:

    enclosure_line = (
        db.query(models.EnclosureOption)
        .filter(models.EnclosureOption.catalog_ref == enclosure_ref)
        .first()
    )
    enclosure_range = extract_enclosure_range(enclosure_ref)

    if motor_start == "DOL":
        from .ui_desc_func_prot_txt.dol import (
            DESCRIPTION,
            TECHNICAL_CHARACTERISTICS,
            FUNCTIONS,
            PROTECTIONS,
        )
    elif motor_start == "SS":
        if motor_power <= 15:
            from .ui_desc_func_prot_txt.ats01 import (
                DESCRIPTION,
                TECHNICAL_CHARACTERISTICS,
                FUNCTIONS,
                PROTECTIONS,
            )
        else:
            from .ui_desc_func_prot_txt.ats130 import (
                DESCRIPTION,
                TECHNICAL_CHARACTERISTICS,
                FUNCTIONS,
                PROTECTIONS,
            )
    elif motor_start == "VSD":
        from .ui_desc_func_prot_txt.vsd import (
            DESCRIPTION,
            TECHNICAL_CHARACTERISTICS,
            FUNCTIONS,
            PROTECTIONS,
        )

    else:  # ATS01
        from .ui_desc_func_prot_txt.ats01 import (
            DESCRIPTION,
            TECHNICAL_CHARACTERISTICS,
            FUNCTIONS,
            PROTECTIONS,
        )

    mounting_type = enclosure_line.mounting_type if enclosure_line else "wall-mounted"
    material = (
        "Polyester"
        if ("PLA" in enclosure_ref.upper() or "PLM" in enclosure_ref.upper())
        else "Steel"
    )

    TECHNICAL_CHARACTERISTICS = TECHNICAL_CHARACTERISTICS.replace(
        "{{PUMP_COUNT}}", str(pump_count)
    )
    TECHNICAL_CHARACTERISTICS = TECHNICAL_CHARACTERISTICS.replace(
        "{{MOUNTING_TYPE}}", mounting_type
    )
    TECHNICAL_CHARACTERISTICS = TECHNICAL_CHARACTERISTICS.replace(
        "{{MATERIAL}}", material.lower()
    )
    TECHNICAL_CHARACTERISTICS = TECHNICAL_CHARACTERISTICS.replace(
        "{{RANGE}}", enclosure_range
    )

    return DESCRIPTION, TECHNICAL_CHARACTERISTICS, FUNCTIONS, PROTECTIONS
