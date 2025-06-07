import pandas as pd
import numpy as np

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # SMA
    df["SMA_14"] = df["Close"].rolling(window=14).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # EMA & MACD
    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df["Upper_BB"] = df["Close"].rolling(window=20).mean() + 2 * df["Close"].rolling(window=20).std()
    df["Lower_BB"] = df["Close"].rolling(window=20).mean() - 2 * df["Close"].rolling(window=20).std()

    # CCI (Commodity Channel Index)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    sma_tp = tp.rolling(window=20).mean()
    mad = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df['CCI'] = (tp - sma_tp) / (0.015 * mad)

    # ADX (Average Directional Index)
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift()), abs(df['Low'] - df['Close'].shift())))
    df['+DM'] = df['High'].diff()
    df['-DM'] = df['Low'].diff()
    df.loc[df['+DM'] < 0, '+DM'] = 0
    df.loc[df['-DM'] > 0, '-DM'] = 0
    tr14 = df['TR'].rolling(window=14).sum()
    plus_dm14 = df['+DM'].rolling(window=14).sum()
    minus_dm14 = df['-DM'].rolling(window=14).sum()
    plus_di14 = 100 * (plus_dm14 / tr14)
    minus_di14 = 100 * (minus_dm14 / tr14)
    dx = 100 * abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)
    df['ADX'] = dx.rolling(window=14).mean()

    # Stochastic Oscillator
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['Stochastic_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stochastic_D'] = df['Stochastic_K'].rolling(window=3).mean()

    # Williams %R
    df['Williams_%R'] = -100 * ((high_14 - df['Close']) / (high_14 - low_14))

    # OBV (On-Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv

    # ATR (Average True Range)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    return df
