from typing import List
import pandas as pd


def calculate_sma(df: pd.DataFrame, window: int = 20):
    df = df.copy()
    df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()
    return df

def calculate_ema(df: pd.DataFrame, window: int = 20):
    df = df.copy()
    df[f"EMA_{window}"] = df["Close"].ewm(span=window, adjust=False).mean()
    return df

def calculate_rsi(df: pd.DataFrame, window: int = 14):
    df = df.copy()
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df[f"RSI_{window}"] = 100 - (100 / (1 + rs))
    return df
def calculate_macd(df: pd.DataFrame, short_window=12, long_window=26, signal_window=9):
    df = df.copy()
    exp1 = df["Close"].ewm(span=short_window, adjust=False).mean()
    exp2 = df["Close"].ewm(span=long_window, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    df["MACD"] = macd
    df["MACD_signal"] = signal
    df["MACD_histogram"] = macd - signal  # İsteğe bağlı: histogram

    return df
def calculate_zscore(df: pd.DataFrame, window: int = 20):
    df = df.copy()
    rolling_mean = df["Close"].rolling(window=window).mean()
    rolling_std = df["Close"].rolling(window=window).std()
    df["Z_Score"] = (df["Close"] - rolling_mean) / rolling_std
    return df
def calculate_bollinger(df: pd.DataFrame, window: int = 20):
    df = df.copy()
    rolling_mean = df["Close"].rolling(window=window).mean()
    rolling_std = df["Close"].rolling(window=window).std()

    df["Bollinger_Mid"] = rolling_mean
    df["Bollinger_Upper"] = rolling_mean + 2 * rolling_std
    df["Bollinger_Lower"] = rolling_mean - 2 * rolling_std
    return df
def calculate_all_indicators(hist, selected_indicators: List[str]):
    if "sma" in selected_indicators:
        hist = calculate_sma(hist)
    if "ema" in selected_indicators:
        hist = calculate_ema(hist)
    if "rsi" in selected_indicators:
        hist = calculate_rsi(hist)
    if "macd" in selected_indicators:
        hist = calculate_macd(hist)
    if "z_score" in selected_indicators:
        hist = calculate_zscore(hist)
    if "bollinger" in selected_indicators:
        hist = calculate_bollinger(hist)

    #  Debug çıktısı
    print("Kolonlar:", hist.columns.tolist())
    print("Son satır:", hist.tail(1).to_dict(orient="records"))

    return hist




def extract_latest_values(hist: pd.DataFrame) -> dict:
    available_cols = hist.columns

    field_map = {
        "Close": "close",
        "SMA_20": "sma",
        "EMA_20": "ema",
        "RSI_14": "rsi",
        "MACD": "macd",
        "MACD_signal": "macd_signal",
        "Z_Score": "z_score",
        "Bollinger_Upper": "bollinger_upper",
        "Bollinger_Lower": "bollinger_lower"
    }

    latest = hist.iloc[-1]  # dropna() kaldırıldı
    result = {}

    for col, label in field_map.items():
        if col in available_cols and pd.notna(latest[col]):
            result[label] = round(latest[col], 2) if "MACD" not in col else round(latest[col], 4)

    return result


def generate_signals(data):
    close = data.get("close")
    signals = {}

    if "macd" in data and "macd_signal" in data:
        signals["macd"] = "Buy" if data["macd"] > data["macd_signal"] else "Sell" if data["macd"] < data["macd_signal"] else "Neutral"

    if "sma" in data:
        signals["sma"] = "Buy" if close < data["sma"] else "Sell" if close > data["sma"] else "Neutral"

    if "ema" in data:
        signals["ema"] = "Buy" if close < data["ema"] else "Sell" if close > data["ema"] else "Neutral"

    if "rsi" in data:
        signals["rsi"] = "Buy" if data["rsi"] < 35 else "Sell" if data["rsi"] > 65 else "Neutral"

    if "z_score" in data:
        signals["z_score"] = "Buy" if data["z_score"] < -2 else "Sell" if data["z_score"] > 2 else "Neutral"

    if "bollinger_lower" in data and "bollinger_upper" in data:
        signals["bollinger"] = "Buy" if close < data["bollinger_lower"] else "Sell" if close > data["bollinger_upper"] else "Neutral"

    return signals

def calculate_weighted_decision(signals):
    weights = {
        "macd": 1.5,
        "sma": 1.0,
        "ema": 1.0,
        "rsi": 1.0,
        "z_score": 0.7,
        "bollinger": 0.8
    }

    buy_score = 0.0
    sell_score = 0.0

    for key, signal in signals.items():
        weight = weights.get(key, 1.0)
        if signal == "Buy":
            buy_score += weight
        elif signal == "Sell":
            sell_score += weight

    total = buy_score + sell_score
    if total == 0:
        return {"signal": "Neutral", "confidence": 0.0}
    elif buy_score > sell_score:
        return {"signal": "Buy", "confidence": round(buy_score / total, 2)}
    elif sell_score > buy_score:
        return {"signal": "Sell", "confidence": round(sell_score / total, 2)}
    else:
        return {"signal": "Neutral", "confidence": 0.5}
