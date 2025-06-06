from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.auth_service import get_current_user
from app.services.history_service import get_user_history

router = APIRouter()

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    return get_user_history(db, current_user["username"], limit)
