import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd

def plot_stock_chart(data: pd.DataFrame, symbol: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(data['date'], data['close'], label='Close Price')
    ax.plot(data['date'], data['sma'], label='SMA', linestyle='--')
    ax.plot(data['date'], data['bollinger_upper'], label='Bollinger Upper', linestyle=':')
    ax.plot(data['date'], data['bollinger_lower'], label='Bollinger Lower', linestyle=':')

    ax.set_title(f"{symbol} Stock Price Chart")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer
