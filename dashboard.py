import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from data import get_nifty_data
from indicators import add_indicators
from strategy import generate_signal
from live_data import get_live_price

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

live_price = get_live_price()

chart_data = data.tail(250)

fig = go.Figure()

# Candlestick
fig.add_trace(
    go.Candlestick(
    x=chart_data.index,
    open=chart_data["Open"],
    high=chart_data["High"],
    low=chart_data["Low"],
    close=chart_data["Close"],
    name="NIFTY"
)
)

# EMA20
fig.add_trace(
    go.Scatter(
        x=chart_data.index,
        y=chart_data["EMA20"],
        mode="lines",
        name="EMA20"
    )
)

# EMA50
fig.add_trace(
    go.Scatter(
        x=chart_data.index,
        y=chart_data["EMA50"],
        mode="lines",
        name="EMA50"
    )
)

# ==========================
# BUY MARKERS
# ==========================

buy_data = chart_data[chart_data["BUY_MARKER"] == "BUY"]

fig.add_trace(
    go.Scatter(
        x=buy_data.index,
        y=buy_data["Low"] - 5,
        mode="markers",
        name="BUY",
        marker=dict(
            symbol="triangle-up",
            size=12,
            color="lime"
        )
    )
)

# ==========================
# SELL MARKERS
# ==========================

sell_data = chart_data[chart_data["SELL_MARKER"] == "SELL"]

fig.add_trace(
    go.Scatter(
        x=sell_data.index,
        y=sell_data["High"] + 5,
        mode="markers",
        name="SELL",
        marker=dict(
            symbol="triangle-down",
            size=12,
            color="red"
        )
    )
)

fig.update_layout(
    height=650,
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    title="Live NIFTY Chart"
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Live NIFTY (Upstox)",
    f"{live_price:.2f}"
)

c2.metric(
    "Chart Close",
    f"{latest['Close']:.2f}"
)

c3.metric(
    "AI Score",
    int(latest["AI_SCORE"])
)

c4.metric(
    "Confidence",
    int(latest["CONFIDENCE"])
)

signal = latest["Signal"]

if signal == "BUY":
    signal_text = "🟢 BUY"

elif signal == "SELL":
    signal_text = "🔴 SELL"

else:
    signal_text = "🟡 HOLD"

c5.metric(
    "Signal",
    signal_text
)

st.plotly_chart(fig, width="stretch")

st.subheader("🧠 AI Decision Reason")

reasons = []

# EMA
if latest["EMA20"] > latest["EMA50"]:
    reasons.append("✅ EMA20 > EMA50 (Bullish)")
else:
    reasons.append("❌ EMA20 < EMA50 (Bearish)")

# MACD
if latest["MACD"] > latest["MACD_SIGNAL"]:
    reasons.append("✅ MACD Bullish")
else:
    reasons.append("❌ MACD Bearish")

# RSI
if latest["RSI"] >= 50:
    reasons.append(f"✅ RSI = {latest['RSI']:.1f}")
else:
    reasons.append(f"❌ RSI = {latest['RSI']:.1f}")

# ADX
if latest["ADX"] >= 25:
    reasons.append(f"✅ ADX = {latest['ADX']:.1f}")
else:
    reasons.append(f"❌ ADX = {latest['ADX']:.1f}")

# AI Score
reasons.append(f"🤖 AI Score = {int(latest['AI_SCORE'])}")

for reason in reasons:
    st.write(reason)

st.subheader("📊 AI Probability")

buy_probability = int((latest["AI_SCORE"] + latest["CONFIDENCE"]) / 2)

sell_probability = 100 - buy_probability

st.write("### 🟢 BUY Probability")
st.progress(buy_probability)

st.write(f"{buy_probability}%")

st.write("### 🔴 SELL Probability")
st.progress(sell_probability)

st.write(f"{sell_probability}%")

st.subheader("Market Status")

st.write("Trend :", latest["MARKET_STATE"])

st.write("Entry :", latest["ENTRY_QUALITY"])

st.write("Position Size :", latest["POSITION_SIZE"], "%")

st.subheader("📈 Trading Performance")

if os.path.exists("trade_history.csv"):

    trades = pd.read_csv("trade_history.csv")

    total_trades = len(trades)

    if total_trades > 0:

        wins = len(trades[trades["Profit"] > 0])

        losses = len(trades[trades["Profit"] <= 0])

        win_rate = (wins / total_trades) * 100

        total_profit = trades["Profit"].sum()

        gross_profit = trades[trades["Profit"] > 0]["Profit"].sum()

        gross_loss = abs(
            trades[trades["Profit"] < 0]["Profit"].sum()
        )

        if gross_loss == 0:
            profit_factor = 0
        else:
            profit_factor = gross_profit / gross_loss

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Net Profit",
            f"₹{total_profit:.2f}"
        )

        c2.metric(
            "🎯 Win Rate",
            f"{win_rate:.1f}%"
        )

        c3.metric(
            "📈 Total Trades",
            total_trades
        )

        c4.metric(
            "⚡ Profit Factor",
            f"{profit_factor:.2f}"
        )

st.subheader("📋 Recent Trades")

st.subheader("📈 Equity Curve")

if os.path.exists("trade_history.csv"):

    trades = pd.read_csv("trade_history.csv")

    if "Profit" in trades.columns:

        trades["Equity"] = 100000 + trades["Profit"].cumsum()

        st.line_chart(
            trades["Equity"]
        )

if os.path.exists("trade_history.csv"):

    trades = pd.read_csv("trade_history.csv")

    st.dataframe(
        trades.tail(10),
        use_container_width=True
    )

else:

    st.info("No trades available yet.")