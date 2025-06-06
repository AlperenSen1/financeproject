from typing import List, Optional
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
def analyze(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    indicators: Optional[List[str]] = Query(default=["sma", "ema", "rsi", "macd", "z_score", "bollinger"]),
    period: Optional[str] = "6mo",
    interval: Optional[str] = "1d"
):
    try:
        #  Eğer "indicators=sma,rsi" şeklinde tek string geldiyse split et
        if indicators and len(indicators) == 1 and "," in indicators[0]:
            indicators = indicators[0].split(",")

        ticker = yf.Ticker(symbol)

        # Tarih aralığı varsa onu kullan, yoksa period
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
        else:
            hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"error": "No data found."}

        hist.reset_index(inplace=True)
        hist["Date"] = hist["Date"].astype(str)

        # DEBUG BAŞLANGIÇ
        print(" MANUEL ANALIZ ÇAĞRISI:", symbol)
        print(" Seçilen Göstergeler:", indicators)
        # DEBUG BİTİŞ

        # Seçilen göstergelere göre analiz yap
        hist = stock_analysis.calculate_all_indicators(hist, selected_indicators=indicators)

        # DEBUG
        print(" Kolonlar:", hist.columns.tolist())
        print(" Son satır:", hist.tail(1).to_dict(orient="records"))

        latest_values = stock_analysis.extract_latest_values(hist)

        # DEBUG
        print(" latest_values:", latest_values)

        signals = stock_analysis.generate_signals(latest_values)

        # DEBUG
        print(" signals:", signals)

        decision = stock_analysis.calculate_weighted_decision(signals)

        return {
            "symbol": symbol.upper(),
            "latest": latest_values,
            "signals": signals,
            "final_decision": decision
        }

    except Exception as e:
        print(" HATA:", str(e))
        return {"error": str(e)}
