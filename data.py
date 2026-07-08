import yfinance as yf
import pandas as pd


# ==========================
# 5 Minute Data
# ==========================

def get_nifty_data():

    ticker = yf.Ticker("^NSEI")

    data = ticker.history(
        period="5d",
        interval="5m",
        auto_adjust=True
    )

    if data.empty:
        raise Exception("Yahoo Finance returned no data.")

    data = data[[
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]]

    return data, data["Close"]


# ==========================
# 15 Minute Data
# ==========================

def get_nifty_data_15m():

    ticker = yf.Ticker("^NSEI")

    data = ticker.history(
        period="5d",
        interval="15m",
        auto_adjust=True
    )

    if data.empty:
        raise Exception("15 Minute data not found.")

    data = data[[
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]]

    return data