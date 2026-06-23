from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db
from ..schemas import master_data as schemas_master

router = APIRouter(
    prefix="/api/v1",
    tags=["Master Data"],
    dependencies=[Depends(auth.get_current_active_user)],
)


@router.get("/series", response_model=List[schemas_master.Series])
def get_series(db: Session = Depends(get_db)):
    return db.query(models.Series).all()


@router.get("/starter-options", response_model=List[schemas_master.StarterOption])
def get_starter_options(db: Session = Depends(get_db)):
    return db.query(models.StarterOption).all()


@router.get("/enclosures", response_model=List[schemas_master.EnclosureOption])
def get_enclosures(db: Session = Depends(get_db)):
    return db.query(models.EnclosureOption).all()


@router.get("/admin-check")
def admin_check(admin_user: models.User = Depends(auth.get_admin_user)):
    """Simple route to verify if the current user has admin privileges."""
    return {"message": f"Hello Admin {admin_user.username}", "role": admin_user.role}


# more to be added if needed... early version right now
@router.get(
    "/enclosure-options/{pump_count}/{motor_start}/{motor_power}",
    response_model=List[schemas_master.EnclosureRecommendation],
)
def get_enclosure_options_for_config(
    db: Session = Depends(get_db),
    pump_count: int = 0,
    motor_start: str = "",
    motor_power: float = 0.0,
):
    def infer_material(catalog_ref: str) -> str:
        reference = (catalog_ref or "").upper()
        return "Polyester" if ("PLA" in reference or "PLM" in reference) else "Steel"

    config_line = (
        db.query(models.Configuration)
        .filter_by(
            load_count=pump_count,
            series_id=motor_start,
            rated_load_power_kw=motor_power,
        )
        .first()
    )
    if not config_line:
        raise HTTPException(status_code=404, detail="Configuration not found")

    recommendation_labels = {
        "recommended": "Recommended",
        "alternative": "Alternative",
        "outdoor_alternative": "Outdoor Alternative",
    }
    recommendation_priority = {
        "recommended": 3,
        "alternative": 2,
        "outdoor_alternative": 1,
    }
    raw_options = [
        ("recommended", config_line.selected_enclosure_ref),
        ("alternative", config_line.alternative_enclosure_ref),
        ("outdoor_alternative", config_line.outdoor_alternative_enclosure_ref),
    ]

    by_reference = {}
    for recommendation_key, reference in raw_options:
        if not reference:
            continue

        candidate = {
            "reference": reference,
            "recommendation_type": recommendation_labels[recommendation_key],
            "material": infer_material(reference),
            "priority": recommendation_priority[recommendation_key],
        }

        existing = by_reference.get(reference)
        if not existing or candidate["priority"] > existing["priority"]:
            by_reference[reference] = candidate

    ordered_options = sorted(
        by_reference.values(),
        key=lambda option: (-option["priority"], option["reference"]),
    )

    return [
        {
            "reference": option["reference"],
            "recommendation_type": option["recommendation_type"],
            "material": option["material"],
        }
        for option in ordered_options
    ]


@router.get(
    "/motor-start-text/{pump_count}/{motor_start}/{motor_power}/{enclosure_ref}",
    response_model=schemas_master.MotorStartTextResponse,
)
def get_motor_start_text(
    db: Session = Depends(get_db),
    pump_count: int = 0,
    motor_start: str = "",
    motor_power: float = 0.0,
    enclosure_ref: str = "",
):
    from ..utils.ui_desc import get_motor_start_text

    textual_data = get_motor_start_text(
        db, pump_count, motor_start, motor_power, enclosure_ref
    )
    if not textual_data:
        raise HTTPException(
            status_code=404, detail="Textual data not found for the given configuration"
        )

    return schemas_master.MotorStartTextResponse(
        description=textual_data[0],
        technical_characteristics=textual_data[1],
        functions=textual_data[2],
        protections=textual_data[3],
    )
