from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import yfinance as yf

from app.services import stock_analysis
from app.auth.auth_service import get_current_user
from app.database.database import get_db
from app.services.history_service import save_analysis
from app.ml.ai_utils import predict_ai_decision

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

# Tüm göstergeler burada
ALL_INDICATORS = [
    "sma", "ema", "rsi", "macd", "z_score", "bollinger",
    "cci", "adx", "stochastic", "williams", "obv", "atr"
]

# ✅ Hafif analiz için - sadece frontend grafik veya hızlı veri gösterimi için
@router.get("/{symbol}")
def get_stock_data(
    symbol: str,
    period: Optional[str] = "1y",
    interval: Optional[str] = "1d"
):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"error": "No data found for this symbol."}

        hist.reset_index(inplace=True)
        hist["Date"] = hist["Date"].astype(str)

        hist = stock_analysis.calculate_sma(hist)
        hist = stock_analysis.calculate_ema(hist)
        hist = stock_analysis.calculate_rsi(hist)
        hist = stock_analysis.calculate_macd(hist)

        return hist[[
            "Date", "Close", "SMA_20", "EMA_20", "RSI_14", "MACD", "MACD_signal"
        ]].dropna().to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


# ✅ Tüm göstergelerle AI destekli tam analiz
@router.get("/analyze/{symbol}")
def analyze(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: Optional[str] = "6mo",
    interval: Optional[str] = "1d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        ticker = yf.Ticker(symbol)
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
        else:
            hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"error": "No data found."}

        hist.reset_index(inplace=True)
        hist["Date"] = hist["Date"].astype(str)

        print(" MANUEL ANALIZ ÇAĞRISI:", symbol)

        # Tüm teknik göstergeleri hesapla
        hist = stock_analysis.calculate_all_indicators(hist, selected_indicators=ALL_INDICATORS)
        latest_values = stock_analysis.extract_latest_values(hist)
        signals = stock_analysis.generate_signals(latest_values)
        decision = stock_analysis.calculate_weighted_decision(signals)

        result = {
            "symbol": symbol.upper(),
            "latest": latest_values,
            "signals": signals,
            "final_decision": decision
        }

        # AI tahmini
        try:
            ai_result = predict_ai_decision(hist)
            result["ai"] = ai_result

        except Exception as ai_error:
            print(f" AI tahmini başarısız: {ai_error}")
            result["ai"] = {
                "error": "AI prediction failed"
            }

        # Veritabanına analiz kaydı
        save_analysis(
            db=db,
            username=current_user["username"],
            symbol=symbol,
            indicators=ALL_INDICATORS,
            result=result
        )

        return result

    except Exception as e:
        print(" HATA:", str(e))
        return {"error": str(e)}
