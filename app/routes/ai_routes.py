from fastapi import APIRouter, Depends, HTTPException
from app.auth.auth_service import get_current_user
from app.services.ai_model import predict_ai_signal

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/predict")
def get_ai_prediction(symbol: str, user=Depends(get_current_user)):
    try:
        prediction, confidence = predict_ai_signal(symbol)
        return {
            "symbol": symbol.upper(),
            "ai_prediction": prediction,
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
