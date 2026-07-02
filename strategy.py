from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def generate_signal(data, close):
    data["EMA20"] = EMAIndicator(close, window=20).ema_indicator()
    data["EMA50"] = EMAIndicator(close, window=50).ema_indicator()
    data["RSI"] = RSIIndicator(close, window=14).rsi()

    data["Signal"] = "HOLD"

    buy = (data["EMA20"] > data["EMA50"]) & (data["RSI"] > 55)
    sell = (data["EMA20"] < data["EMA50"]) & (data["RSI"] < 45)

    data.loc[buy, "Signal"] = "BUY"
    data.loc[sell, "Signal"] = "SELL"

    return data