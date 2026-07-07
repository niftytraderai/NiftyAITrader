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


def add_supertrend(data, period=10, multiplier=3):

    hl2 = (data["High"] + data["Low"]) / 2

    atr = data["ATR"]

    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    data["SUPERTREND"] = upperband

    trend = [True]

    for i in range(1, len(data)):

        if data["Close"].iloc[i] > upperband.iloc[i - 1]:
            trend.append(True)

        elif data["Close"].iloc[i] < lowerband.iloc[i - 1]:
            trend.append(False)

        else:
            trend.append(trend[-1])

    data["SUPERTREND_DIRECTION"] = trend

    return data 


def add_vwap(data):

    tp = (data["High"] + data["Low"] + data["Close"]) / 3

    cumulative_tp_vol = (tp * data["Volume"]).cumsum()
    cumulative_vol = data["Volume"].replace(0, 1).cumsum()

    data["VWAP"] = cumulative_tp_vol / cumulative_vol

    return data 

     
def add_volume_spike(data):

    data["AVG_VOLUME"] = data["Volume"].rolling(20).mean()

    data["VOLUME_RATIO"] = (
        data["Volume"] /
        data["AVG_VOLUME"].replace(0, 1)
    )

    data["VOLUME_SPIKE"] = data["VOLUME_RATIO"] >= 1.8

    return data


def add_ai_score(data):

    score = pd.Series(0.0, index=data.index)

    # EMA Trend (0-25)
    ema_gap = ((data["EMA20"] - data["EMA50"]) / data["EMA50"]) * 100
    score += ((ema_gap.clip(0, 0.5) / 0.5) * 25)

    # RSI (0-20)
    score += (
        ((data["RSI"] - 40).clip(0, 20) / 20) * 20
    )

    # ADX (0-20)
    score += (
        ((data["ADX"] - 20).clip(0, 20) / 20) * 20
    )

    # MACD (0-20)
    score += (
        (data["MACD"] > data["MACD_SIGNAL"]).astype(int) * 20
    )

    # SuperTrend (0-15)
    score += (
        data["SUPERTREND_DIRECTION"].astype(int) * 15
    )

    data["AI_SCORE"] = score.clip(0, 100).round(0)

    return data

def add_indicators(data):

    data = add_ema(data)
    data = add_rsi(data)
    data = add_atr(data)
    data = add_adx(data)
    data = add_macd(data)
    data = add_supertrend(data)
    data = add_vwap(data)
    data = add_volume_spike(data)
    data = add_ai_score(data)

    return data