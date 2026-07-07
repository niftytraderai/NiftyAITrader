import pandas as pd


# ==========================
# EMA
# ==========================

def add_ema(data):

    data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()

    data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()

    data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()

    return data


# ==========================
# RSI
# ==========================

def add_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = 100 - (100 / (1 + rs))

    return data


# ==========================
# ATR
# ==========================

def add_atr(data, period=14):

    hl = data["High"] - data["Low"]

    hc = (data["High"] - data["Close"].shift()).abs()

    lc = (data["Low"] - data["Close"].shift()).abs()

    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    data["ATR"] = tr.rolling(period).mean()

    return data


# ==========================
# MAIN
# ==========================

def add_indicators(data):

    data = add_ema(data)

    data = add_rsi(data)

    data = add_atr(data)

    return data