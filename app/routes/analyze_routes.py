# routes/analyze_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import io
import csv
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.database import get_db
from app.services.company_service import get_symbol_by_company_name

router = APIRouter()

# Örnek analiz verisi (test amaçlı)
mock_result = {
    "symbol": "AAPL",
    "latest": {
        "close": 203.89,
        "sma": 204.2,
        "rsi": 35.53,
        "bollinger_upper": 210.0,
        "bollinger_lower": 190.0
    }
}


from app.plot.plot_utils import generate_sample_plot

import yfinance as yf
import numpy as np
import pandas as pd
from app.plot.plot_utils import generate_sample_plot

def get_analysis_result(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo", interval="1d")

        if hist.empty:
            return None

        close = hist["Close"]
        latest_close = round(close.iloc[-1], 2)

        # Teknik Göstergeler
        sma = round(close.rolling(window=20).mean().iloc[-1], 2)
        ema = round(close.ewm(span=20, adjust=False).mean().iloc[-1], 2)

        delta = close.diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=14).mean()
        avg_loss = pd.Series(loss).rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = round(100 - (100 / (1 + rs.iloc[-1])), 2)

        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = round((exp1 - exp2).iloc[-1], 4)
        macd_signal = round((exp1 - exp2).ewm(span=9, adjust=False).mean().iloc[-1], 4)

        mean = close.rolling(window=20).mean()
        std = close.rolling(window=20).std()
        upper = round(mean.iloc[-1] + 2 * std.iloc[-1], 2)
        lower = round(mean.iloc[-1] - 2 * std.iloc[-1], 2)

        z_score = round((latest_close - mean.iloc[-1]) / std.iloc[-1], 2)

        # Sinyal üretimi
        signals = {
            "sma": "Buy" if latest_close > sma else "Sell",
            "ema": "Buy" if latest_close > ema else "Sell",
            "rsi": "Buy" if rsi < 30 else "Sell" if rsi > 70 else "Neutral",
            "macd": "Buy" if macd > macd_signal else "Sell",
            "z_score": "Buy" if z_score < -1 else "Sell" if z_score > 1 else "Neutral",
            "bollinger": "Buy" if latest_close < lower else "Sell" if latest_close > upper else "Neutral",
        }

        buy_count = list(signals.values()).count("Buy")
        sell_count = list(signals.values()).count("Sell")

        if buy_count > sell_count:
            decision = "Buy"
            confidence = round(buy_count / len(signals), 2)
        elif sell_count > buy_count:
            decision = "Sell"
            confidence = round(sell_count / len(signals), 2)
        else:
            decision = "Neutral"
            confidence = 0.5

        # Grafik üretimi
        generate_sample_plot(symbol)

        return {
            "symbol": symbol.upper(),
            "latest": {
                "close": latest_close,
                "sma": sma,
                "ema": ema,
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_signal,
                "z_score": z_score,
                "bollinger_upper": upper,
                "bollinger_lower": lower
            },
            "signals": signals,
            "final_decision": {
                "signal": decision,
                "confidence": confidence
            },
            "chart_url": f"/plots/{symbol}.png"
        }

    except Exception as e:
        print(f"[ERROR] Analysis failed for {symbol}: {e}")
        return None




@router.get("/download/csv/{symbol}")
def download_csv(symbol: str):
    result = get_analysis_result(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis result found.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in result["latest"].items():
        writer.writerow([key, value])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={symbol}_analysis.csv"}
    )


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from app.plot.plot_utils import generate_sample_plot


@router.get("/download/pdf/{symbol}")
def download_pdf(symbol: str):
    generate_sample_plot(symbol)  # PNG üret

    result = get_analysis_result(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis result found.")

    file_path = f"{symbol}_analysis.pdf"
    plot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plots", f"{symbol}.png"))

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Başlık
    c.drawString(100, 750, f"Analysis Report for {symbol}")

    # Yazılar
    y = 720
    for key, value in result["latest"].items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20

    # Grafik en alta
    if os.path.exists(plot_path):
        c.drawImage(ImageReader(plot_path), 100, 100, width=400, preserveAspectRatio=True)

    c.save()
    return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")





@router.get("/analyze_by_name")
def analyze_by_name(company: str, db: Session = Depends(get_db)):
    result = get_symbol_by_company_name(db, company)
    if not result:
        raise HTTPException(status_code=404, detail="Company not found.")

    symbol = result.symbol
    analysis = get_analysis_result(symbol)
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis result found.")

    return analysis

@router.get("/suggest_companies")
def suggest_companies(q: str, db: Session = Depends(get_db)):
    from app.models.company import Company
    results = db.query(Company).filter(Company.name.ilike(f"%{q}%")).limit(5).all()
    return [{"symbol": r.symbol, "name": r.name} for r in results]


