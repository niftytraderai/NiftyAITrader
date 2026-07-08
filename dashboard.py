import streamlit as st
import pandas as pd

from data import get_nifty_data
from indicators import add_indicators
from strategy import generate_signal

st.set_page_config(
    page_title="Nifty AI Trader",
    layout="wide"
)

st.title("🤖 Nifty AI Trader V5")

st.write("Professional AI Paper Trading Dashboard")

data, close = get_nifty_data()

data = add_indicators(data)

data["HTF_BULLISH"] = (
    data["EMA20"] > data["EMA50"]
)

data = generate_signal(data, close)

latest = data.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "NIFTY",
    f"{latest['Close']:.2f}"
)

c2.metric(
    "AI Score",
    int(latest["AI_SCORE"])
)

c3.metric(
    "Confidence",
    int(latest["CONFIDENCE"])
)

c4.metric(
    "Signal",
    latest["Signal"]
)

st.subheader("Market Status")

st.write("Trend :", latest["MARKET_STATE"])

st.write("Entry :", latest["ENTRY_QUALITY"])

st.write("Position Size :", latest["POSITION_SIZE"], "%")

st.line_chart(data["Close"])

st.subheader("Latest Candles")

st.dataframe(

    data[[
        "Close",
        "AI_SCORE",
        "CONFIDENCE",
        "Signal"
    ]].tail(20)

)