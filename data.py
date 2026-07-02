import yfinance as yf

def get_nifty_data():
    data = yf.download("^NSEI", period="3mo", interval="1d")

    # MultiIndex handle karo
    close = data[("Close", "^NSEI")]

    return data, close