from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from app.auth.auth_service import authenticate_user, create_access_token, get_current_user
from app.auth.users import fake_users_db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# 🔐 LOGIN
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": form_data.username, "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 📝 REGISTER
class RegisterForm(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(form: RegisterForm):
    if form.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db[form.username] = {
        "username": form.username,
        "password": form.password,
        "role": "free"  # Yeni kayıt olanlar free başlar
    }
    return {"message": "User registered successfully"}

# ⭐ PREMIUM-ONLY ENDPOINT
@router.get("/premium-only")
async def premium_only(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "premium":
        raise HTTPException(status_code=403, detail="Premium membership required")
    return {"message": f"Welcome, premium user {current_user['username']}!"}
