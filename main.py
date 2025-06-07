from fastapi.middleware.cors import CORSMiddleware

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from app.routes.stock_routes import router as stock_router
from app.routes.auth_routes import router as auth_router
from app.routes.plot_routes import router as plot_router

from app.config import settings
from app.logging_config import logger
from app.auth.auth_service import authenticate_user, create_access_token
from app.services.scheduler import start_scheduler  # ✅ sadece 1 kez import edildi

import jwt

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "Authentication endpoints"},
        {"name": "Stocks", "description": "Stock-related operations"},
        {"name": "Plots", "description": "Chart and plot endpoints"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 🔁 ROUTER EKLEME
app.include_router(stock_router)
app.include_router(auth_router)
app.include_router(plot_router)

# 🌐 KÖK ENDPOINT
@app.get("/", tags=["General"])
def root():
    logger.info("Root endpoint called.")
    return {"message": f"{settings.app_name} is running."}

# 📦 JWT TOKEN ALMA ENDPOINT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="JWT")

@app.get("/secure-data", tags=["Auth"])
def secure_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "very-secret-key", algorithms=["HS256"])
        username = payload.get("sub")
        role = payload.get("role")
        return {"message": f"Hello {username}, your role is {role}."}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

# 🛡️ SWAGGER BEARER TOKEN UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version="1.0.0",
        description="API for accessing stock data and user authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path].values():
            method.setdefault("security", [{"OAuth2PasswordBearer": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 📄 REQUEST LOGGING
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"New request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# 🚀 SCHEDULER BAŞLAT
import threading

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=start_scheduler, daemon=True).start()



from app.routes import news_routes
app.include_router(news_routes.router)

from app.routes import history_routes
app.include_router(history_routes.router)

from app.routes.analyze_routes import router as analyze_router
app.include_router(analyze_router)

from fastapi.staticfiles import StaticFiles
import os

if not os.path.exists("app/plots"):
    os.makedirs("app/plots")

app.mount("/plots", StaticFiles(directory="app/plots"), name="plots")

from app.routes.company_routes import router as company_router
app.include_router(company_router)

from app.routes import ai_routes
app.include_router(ai_routes.router)






