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

import matplotlib.pyplot as plt
import os

def generate_sample_plot(symbol: str):
    # Örnek veri
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 15, 25, 30]

    plt.figure(figsize=(6, 4))
    plt.plot(x, y, label="Sample Data")
    plt.title(f"{symbol} Stock Sample Plot")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.legend()
    plt.grid(True)

    # Kayıt yolu
    save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plots", f"{symbol}.png"))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()

