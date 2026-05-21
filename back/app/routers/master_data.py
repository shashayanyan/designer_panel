from typing import Dict, List

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
    response_model=Dict[str, str],
)
def get_enclosure_options_for_config(
    db: Session = Depends(get_db),
    pump_count: int = 0,
    motor_start: str = "",
    motor_power: float = 0.0,
):
    # Implementation for fetching enclosure options based on configuration
    # print(f"Fetching enclosure options for pumps={pump_count}, motor_start={motor_start}, motor_power={motor_power}")
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
    res = {
        "recommended": config_line.selected_enclosure_ref,
        "alternative": config_line.alternative_enclosure_ref,
        "outdoor_alternative": config_line.outdoor_alternative_enclosure_ref,
    }
    # print(res)
    # get rid of null/empty/duplicate values before returning
    res = {k: v for k, v in res.items() if v}
    return res
