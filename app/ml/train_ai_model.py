import os
import yfinance as yf
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from app.services.indicators import add_technical_indicators

def label_row(pct):
    if pct > 0.03:
        return "Buy"
    elif pct < -0.03:
        return "Sell"
    else:
        return "Neutral"

symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "PG", "UNH", "HD", "MA", "BAC", "XOM", "DIS", "KO", "PEP",
    "ADBE", "CSCO", "CMCSA", "VZ", "T", "ABT", "NFLX", "COST", "PFE", "INTC",
    "CRM", "WMT", "MRK", "NKE", "MCD", "WFC", "ORCL", "CVX", "QCOM", "UPS"
]

all_data = []

for symbol in symbols:
    try:
        print(f" İşleniyor: {symbol}")
        df = yf.download(symbol, start="2015-01-01", end="2024-12-31")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty or "Close" not in df.columns:
            print(f" {symbol} verisi alınamadı.")
            continue

        df = add_technical_indicators(df)
        df["Future_Close"] = df["Close"].shift(-5)
        df = df.dropna(subset=["Close", "Future_Close"]).copy()
        df["Pct_Change"] = (df["Future_Close"] - df["Close"]) / df["Close"]
        df["Label"] = df["Pct_Change"].apply(label_row)

        selected = df[[
            "Close", "SMA_14", "RSI_14", "MACD", "Signal", "Upper_BB", "Lower_BB",
            "CCI", "ADX", "Stochastic_K", "Stochastic_D", "Williams_%R", "OBV", "ATR", "Label"
        ]].dropna()

        all_data.append(selected)

    except Exception as e:
        print(f" {symbol} hatası: {e}")

if not all_data:
    print(" Eğitim için yeterli veri yok.")
    exit()

dataset = pd.concat(all_data)
X = dataset.drop("Label", axis=1)
y = dataset["Label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n Accuracy: {round(acc, 3)}")
print(classification_report(y_test, y_pred))

model_path = os.path.join(os.path.dirname(__file__), "ai_stock_model.joblib")
joblib.dump(model, model_path)
print(f" Model kaydedildi: {model_path}")
