import yfinance as yf
import pandas as pd


def get_nifty_data():

    data = yf.download(
        "^NSEI",
        period="60d",
        interval="5m",
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if data.empty:
        raise Exception("Yahoo Finance returned no data.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data[[
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]]

    return data, data["Close"]