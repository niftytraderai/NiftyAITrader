import pandas as pd


def add_market_structure(data):

    # Previous Swing High / Low
    data["PREV_HIGH"] = data["High"].rolling(10).max().shift(1)
    data["PREV_LOW"] = data["Low"].rolling(10).min().shift(1)

    # Break Of Structure
    data["BOS_BULL"] = data["Close"] > data["PREV_HIGH"]
    data["BOS_BEAR"] = data["Close"] < data["PREV_LOW"]

    # ==========================
    # Change Of Character (CHOCH)
    # ==========================

    data["CHOCH_BULL"] = (
        data["BOS_BULL"] &
        (data["EMA20"] > data["EMA50"])
    )

    data["CHOCH_BEAR"] = (
        data["BOS_BEAR"] &
        (data["EMA20"] < data["EMA50"])
    )

    data["HTF_BULLISH"] = data["EMA200"] < data["Close"]
    data["HTF_BEARISH"] = data["EMA200"] > data["Close"]

    return data