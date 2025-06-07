# app/ml/ai_utils.py

import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ai_stock_model.joblib")

def predict_ai_decision(df: pd.DataFrame):
    # Modeli yükle
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("AI modeli bulunamadı.")

    model = joblib.load(MODEL_PATH)

    # Tahmin için en son satırı al
    latest_row = df.iloc[[-1]]

    # Label yoksa sadece X sütunlarını al
    features = [
        "Close", "SMA_14", "RSI_14", "MACD", "Signal", "Upper_BB", "Lower_BB",
        "CCI", "ADX", "Stochastic_K", "Stochastic_D", "Williams_%R", "OBV", "ATR"
    ]

    # Eksik sütun var mı kontrol et
    missing = [col for col in features if col not in latest_row.columns]
    if missing:
        raise ValueError(f"Eksik sütunlar: {missing}")

    # Tahmin yap
    prediction = model.predict(latest_row[features])[0]
    proba = model.predict_proba(latest_row[features])[0]

    confidence = round(max(proba), 2)

    return {
        "signal": prediction,
        "confidence": confidence
    }
