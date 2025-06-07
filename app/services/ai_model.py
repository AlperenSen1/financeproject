import yfinance as yf
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple

#  Eğitimli modeli yükle
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "ai_stock_model.joblib")
model: RandomForestClassifier = joblib.load(MODEL_PATH)

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["SMA_14"] = df["Close"].rolling(window=14).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Upper_BB"] = df["Close"].rolling(window=20).mean() + 2 * df["Close"].rolling(window=20).std()
    df["Lower_BB"] = df["Close"].rolling(window=20).mean() - 2 * df["Close"].rolling(window=20).std()
    return df

def predict_ai_signal(symbol: str) -> Tuple[str, float]:
    df = yf.download(symbol, period="6mo", interval="1d", auto_adjust=True)

    if df.empty or "Close" not in df.columns:
        return "Unknown", 0.0

    df = calculate_indicators(df)
    df = df.dropna().copy()

    try:
        latest = df.iloc[-1][["Close", "SMA_14", "RSI_14", "MACD", "Signal", "Upper_BB", "Lower_BB"]]
        input_data = latest.values.reshape(1, -1)
        prediction = model.predict(input_data)[0]
        confidence = max(model.predict_proba(input_data)[0])
        return prediction, round(confidence, 2)
    except Exception as e:
        print(f" Prediction error: {e}")
        return "Error", 0.0
