import yfinance as yf

def get_nifty_data():
    data = yf.download("^NSEI", period="5d", interval="5m")

    # MultiIndex handle
    close = data[("Close", "^NSEI")]
    high = data[("High", "^NSEI")]
    low = data[("Low", "^NSEI")]

    # Simple columns
    data["Close"] = close
    data["High"] = high
    data["Low"] = low

    return data, close