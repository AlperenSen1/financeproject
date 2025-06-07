from sqlalchemy.orm import Session
from app.models.company import Company

def get_symbol_by_company_name(db: Session, name: str):
    return db.query(Company).filter(Company.name.ilike(f"%{name}%")).first()
