from fastapi import APIRouter, Depends
from app.services.news_service import get_latest_news
from app.auth.auth_service import get_current_user

router = APIRouter()

@router.get("/news")
def news_route(user: dict = Depends(get_current_user)):
    return {"news": get_latest_news()}
