import pandas as pd

# ==========================
# 5 Minute Data
# ==========================

def get_nifty_data():

    data = pd.read_csv("historical_spot.csv")

    data["datetime"] = pd.to_datetime(data["datetime"])

    data.set_index("datetime", inplace=True)

    data.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }, inplace=True)

    return data, data["Close"]


# ==========================
# 15 Minute Data
# ==========================

def get_nifty_data_15m():

    data = pd.read_csv("historical_spot.csv")

    data["datetime"] = pd.to_datetime(data["datetime"])

    data.set_index("datetime", inplace=True)

    data.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }, inplace=True)

    # 1-minute data ko 15-minute candles me convert karo
    data_15m = data.resample("15min").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()

    return data_15m