from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.company import Company

router = APIRouter()

@router.get("/companies", tags=["Companies"])
def get_all_companies(db: Session = Depends(get_db)):
    return db.query(Company).limit(1000).all()
