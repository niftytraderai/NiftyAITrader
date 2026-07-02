import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Nifty AI Trader", layout="wide")

st.title("📈 Nifty AI Trader Dashboard")

# Live Nifty Price
data = yf.download("^NSEI", period="5d", interval="1m")
price = float(data["Close"].iloc[-1])

st.metric("Nifty Live Price", f"{price:.2f}")

st.divider()

try:
    trades = pd.read_csv("trades.csv")

    st.subheader("Trade History")
    st.dataframe(trades)

    total_profit = trades["Profit"].sum()

    st.metric("Total Profit", f"₹ {total_profit:.2f}")

except:
    st.warning("No trades found.")