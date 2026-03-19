from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..schemas import master_data as schemas_master
from ..database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["Master Data"],
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

# more to be added if needed... early version right now