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
def calculate_all_indicators(hist):
    hist = calculate_sma(hist)
    hist = calculate_ema(hist)
    hist = calculate_rsi(hist)
    hist = calculate_macd(hist)
    hist = calculate_zscore(hist)
    hist = calculate_bollinger(hist)
    return hist


def extract_latest_values(hist):
    latest = hist[[
        "Close", "SMA_20", "EMA_20", "RSI_14", "MACD", "MACD_signal",
        "Z_Score", "Bollinger_Upper", "Bollinger_Lower"
    ]].dropna().iloc[-1]

    return {
        "close": round(latest["Close"], 2),
        "sma": round(latest["SMA_20"], 2),
        "ema": round(latest["EMA_20"], 2),
        "rsi": round(latest["RSI_14"], 2),
        "macd": round(latest["MACD"], 4),
        "macd_signal": round(latest["MACD_signal"], 4),
        "z_score": round(latest["Z_Score"], 2),
        "bollinger_upper": round(latest["Bollinger_Upper"], 2),
        "bollinger_lower": round(latest["Bollinger_Lower"], 2)
    }
def generate_signals(data):
    close = data["close"]
    signals = {
        "macd": "Buy" if data["macd"] > data["macd_signal"] else "Sell" if data["macd"] < data["macd_signal"] else "Neutral",
        "sma": "Buy" if close < data["sma"] else "Sell" if close > data["sma"] else "Neutral",
        "ema": "Buy" if close < data["ema"] else "Sell" if close > data["ema"] else "Neutral",
        "rsi": "Buy" if data["rsi"] < 35 else "Sell" if data["rsi"] > 65 else "Neutral",
        "z_score": "Buy" if data["z_score"] < -2 else "Sell" if data["z_score"] > 2 else "Neutral",
        "bollinger": "Buy" if close < data["bollinger_lower"] else "Sell" if close > data["bollinger_upper"] else "Neutral"
    }
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
