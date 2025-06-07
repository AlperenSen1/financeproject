from fastapi import APIRouter
from typing import Optional
import yfinance as yf
import pandas as pd
import os
from app.services.stock_analysis import calculate_all_indicators

router = APIRouter(prefix="/screener", tags=["Screener"])

# 🔽 CSV'den sembol listesi çek
def load_symbols_from_csv():
    csv_path = os.path.join(os.path.dirname(__file__), "../data/companylist.csv")
    df = pd.read_csv(csv_path)
    return df["Symbol"].dropna().unique().tolist()

STOCK_SYMBOLS = load_symbols_from_csv()

@router.get("/")
def screener(
    rsi_lt: Optional[float] = None,
    macd_gt: Optional[float] = None,
    sma_lt: Optional[float] = None,
    sma_gt: Optional[float] = None,
):
    results = []

    for symbol in STOCK_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo", interval="1d")

            if df.empty:
                continue

            df = calculate_all_indicators(df, selected_indicators=["sma", "rsi", "macd"])
            latest = df.iloc[-1]

            if rsi_lt is not None and latest.get("RSI_14", 100) >= rsi_lt:
                continue
            if macd_gt is not None and latest.get("MACD", -999) <= macd_gt:
                continue
            if sma_lt is not None and latest.get("SMA_14", 9999) >= sma_lt:
                continue
            if sma_gt is not None and latest.get("SMA_14", -1) <= sma_gt:
                continue

            results.append({
                "symbol": symbol,
                "rsi": round(latest.get("RSI_14", 0), 2),
                "macd": round(latest.get("MACD", 0), 2),
                "sma": round(latest.get("SMA_14", 0), 2),
                "close": round(latest.get("Close", 0), 2)
            })

        except Exception:
            continue

    return results
