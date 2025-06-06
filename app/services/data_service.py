import yfinance as yf
from app.models.stock_model import StockResponse

def fetch_stock_data(symbol: str) -> StockResponse:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    return StockResponse(
        symbol=symbol.upper(),
        shortName=info.get("shortName"),
        currentPrice=info.get("currentPrice"),
        currency=info.get("currency"),
        peRatio=info.get("trailingPE"),               # F/K Oranı
        pbRatio=info.get("priceToBook"),              # PD/DD Oranı
        returnOnEquity=info.get("returnOnEquity")     # Özkaynak Karlılığı
    )
import yfinance as yf
import pandas as pd
import numpy as np
from app.models.stock_model import TechnicalAnalysisResponse

def calculate_rsi(close_prices: pd.Series, period: int = 14) -> float:
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def fetch_technical_analysis(symbol: str) -> TechnicalAnalysisResponse:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="30d")

    close_prices = hist["Close"]

    rsi_value = calculate_rsi(close_prices)
    ma_7 = close_prices.rolling(window=7).mean().iloc[-1]
    ma_14 = close_prices.rolling(window=14).mean().iloc[-1]

    return TechnicalAnalysisResponse(
        symbol=symbol.upper(),
        rsi=rsi_value,
        moving_average_7=round(ma_7, 2),
        moving_average_14=round(ma_14, 2),
        close_prices=[round(p, 2) for p in close_prices[-14:]]  # Son 14 günü listele
    )
import yfinance as yf
import pandas as pd

def get_stock_data_for_plot(symbol: str) -> pd.DataFrame:
    df = yf.download(symbol, period="6mo")

    if df.empty:
        return None

    df = df.tail(100).copy()
    df['sma'] = df['Close'].rolling(window=20).mean()
    df['std'] = df['Close'].rolling(window=20).std()
    df['bollinger_upper'] = df['sma'] + 2 * df['std']
    df['bollinger_lower'] = df['sma'] - 2 * df['std']
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
    return df[['date', 'close', 'sma', 'bollinger_upper', 'bollinger_lower']]
