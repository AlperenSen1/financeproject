from fastapi import APIRouter, Query, Depends
from typing import Optional
import yfinance as yf

from app.services import stock_analysis
from app.auth.auth_service import get_current_user

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

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
            "Date",
            "Close",
            "SMA_20",
            "EMA_20",
            "RSI_14",
            "MACD",
            "MACD_signal"
        ]].dropna().to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}


@router.get("/analyze/{symbol}")
def analyze_stock(
    symbol: str,
    period: Optional[str] = Query(None, description="Example: 6mo, 1y, etc."),
    interval: Optional[str] = "1d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        ticker = yf.Ticker(symbol)

        # 🎯 Tarih aralığı varsa onu kullan
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
        else:
            hist = ticker.history(period=period or "6mo", interval=interval)

        if hist.empty:
            return {"error": "No data found."}

        hist.reset_index(inplace=True)
        hist["Date"] = hist["Date"].astype(str)

        hist = stock_analysis.calculate_all_indicators(hist)
        latest_values = stock_analysis.extract_latest_values(hist)
        signals = stock_analysis.generate_signals(latest_values)
        decision = stock_analysis.calculate_weighted_decision(signals)

        return {
            "symbol": symbol.upper(),
            "latest": latest_values,
            "signals": signals,
            "final_decision": decision
        }

    except Exception as e:
        return {"error": str(e)}
