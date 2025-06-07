from typing import List
import pandas as pd


# --- Basit Göstergeler ---

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
    df["MACD_histogram"] = macd - signal
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


# --- Gelişmiş Göstergeler ---

def calculate_cci(df: pd.DataFrame, window: int = 20):
    df = df.copy()
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    ma = tp.rolling(window=window).mean()
    md = tp.rolling(window=window).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    df["CCI"] = (tp - ma) / (0.015 * md)
    return df


def calculate_obv(df: pd.DataFrame):
    df = df.copy()
    obv = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv
    return df

def calculate_atr(df: pd.DataFrame, window: int = 14):
    df = df.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    tr = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    df["ATR"] = tr.rolling(window=window).mean()
    df.drop(columns=["H-L", "H-PC", "L-PC"], inplace=True)
    return df

def calculate_adx(df: pd.DataFrame, window: int = 14):
    df = df.copy()
    df["TR"] = df[["High", "Low", "Close"]].apply(
        lambda row: max(
            row["High"] - row["Low"],
            abs(row["High"] - row["Close"]),
            abs(row["Low"] - row["Close"])
        ), axis=1
    )
    df["+DM"] = df["High"].diff()
    df["-DM"] = df["Low"].diff().abs()
    df["+DM"] = df["+DM"].where((df["+DM"] > df["-DM"]) & (df["+DM"] > 0), 0.0)
    df["-DM"] = df["-DM"].where((df["-DM"] > df["+DM"]) & (df["-DM"] > 0), 0.0)
    atr = df["TR"].rolling(window=window).mean()
    plus_di = 100 * (df["+DM"].rolling(window=window).mean() / atr)
    minus_di = 100 * (df["-DM"].rolling(window=window).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["ADX"] = dx.rolling(window=window).mean()
    df.drop(columns=["TR", "+DM", "-DM"], inplace=True)
    return df

def calculate_stochastic(df: pd.DataFrame, k_window: int = 14, d_window: int = 3):
    df = df.copy()
    low_min = df["Low"].rolling(window=k_window).min()
    high_max = df["High"].rolling(window=k_window).max()
    df["Stochastic_K"] = 100 * ((df["Close"] - low_min) / (high_max - low_min))
    df["Stochastic_D"] = df["Stochastic_K"].rolling(window=d_window).mean()
    return df

def calculate_williams_r(df: pd.DataFrame, window: int = 14):
    df = df.copy()
    high = df["High"].rolling(window=window).max()
    low = df["Low"].rolling(window=window).min()
    df["Williams_%R"] = -100 * ((high - df["Close"]) / (high - low))
    return df


# --- Master Fonksiyon ---

def calculate_all_indicators(hist: pd.DataFrame, selected_indicators: List[str]) -> pd.DataFrame:
    if not selected_indicators:
        selected_indicators = ["sma", "ema", "rsi", "macd", "bollinger", "z_score"]

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
    if "cci" in selected_indicators:
        hist = calculate_cci(hist)
    if "adx" in selected_indicators:
        hist = calculate_adx(hist)
    if "stochastic" in selected_indicators:
        hist = calculate_stochastic(hist)
    if "williams" in selected_indicators:
        hist = calculate_williams_r(hist)
    if "obv" in selected_indicators:
        hist = calculate_obv(hist)
    if "atr" in selected_indicators:
        hist = calculate_atr(hist)
        # AI modelinin beklediği özel süton isimleriyle eşle
        if "SMA_20" in hist.columns:
            hist["SMA_14"] = hist["SMA_20"]
        if "MACD_signal" in hist.columns:
            hist["Signal"] = hist["MACD_signal"]
        if "Bollinger_Upper" in hist.columns:
            hist["Upper_BB"] = hist["Bollinger_Upper"]
        if "Bollinger_Lower" in hist.columns:
            hist["Lower_BB"] = hist["Bollinger_Lower"]

    return hist


# --- Signal + Decision ---

def extract_latest_values(hist: pd.DataFrame) -> dict:
    available_cols = hist.columns
    latest = hist.iloc[-1]
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
