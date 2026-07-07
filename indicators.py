import pandas as pd


def add_ema(data):

    data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()
    data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()
    data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()

    return data


def add_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = 100 - (100 / (1 + rs))

    return data


def add_atr(data, period=14):

    hl = data["High"] - data["Low"]
    hc = (data["High"] - data["Close"].shift()).abs()
    lc = (data["Low"] - data["Close"].shift()).abs()

    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)

    data["ATR"] = tr.rolling(period).mean()

    return data


def add_adx(data, period=14):

    up_move = data["High"].diff()
    down_move = -data["Low"].diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    atr = data["ATR"]

    plus_di = 100 * (plus_dm.rolling(period).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(period).sum() / atr)

    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di)) * 100

    data["PLUS_DI"] = plus_di
    data["MINUS_DI"] = minus_di
    data["ADX"] = dx.rolling(period).mean()

    return data  


def add_macd(data):

    ema12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema26 = data["Close"].ewm(span=26, adjust=False).mean()

    data["MACD"] = ema12 - ema26
    data["MACD_SIGNAL"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_HIST"] = data["MACD"] - data["MACD_SIGNAL"]

    return data

def add_indicators(data):

    data = add_ema(data)
    data = add_rsi(data)
    data = add_atr(data)
    data = add_adx(data)
    data = add_macd(data)

    return data