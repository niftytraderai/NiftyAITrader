from config import (
    AI_SCORE_MIN,
    CONFIDENCE_MIN,
    ADX_MIN,
    RSI_MIN,
    RSI_MAX
)

def generate_signal(
    data,
    close,
    ai_min=AI_SCORE_MIN,
    confidence_min=CONFIDENCE_MIN,
    adx_min=ADX_MIN,
    rsi_min=RSI_MIN,
    rsi_max=RSI_MAX
):

    data["Signal"] = "HOLD"

    buy = (

        (data["EMA20"] > data["EMA50"]) &

        (data["MACD"] > data["MACD_SIGNAL"]) &

        (data["RSI"] >= rsi_min) &
        (data["RSI"] <= rsi_max) &

        (data["ADX"] >= adx_min) &

        (data["HTF_BULLISH"] == True) &

        (data["AI_SCORE"] >= ai_min) &

        (data["CONFIDENCE"] >= confidence_min)

    )

    sell = (

        (data["EMA20"] < data["EMA50"]) |

        (data["MACD"] < data["MACD_SIGNAL"]) |

        (data["RSI"] < 45)

    )

def generate_signal(
    data,
    close,
    ai_min=AI_SCORE_MIN,
    confidence_min=CONFIDENCE_MIN,
    adx_min=ADX_MIN,
    rsi_min=RSI_MIN,
    rsi_max=RSI_MAX
):

    data["Signal"] = "HOLD"

    buy = (

        (data["EMA20"] > data["EMA50"]) &

        (data["MACD"] > data["MACD_SIGNAL"]) &

        (data["RSI"] >= rsi_min) &
        (data["RSI"] <= rsi_max) &

        (data["ADX"] >= adx_min) &

        (data["HTF_BULLISH"] == True) &

        (data["AI_SCORE"] >= ai_min) &

        (data["CONFIDENCE"] >= confidence_min)

    )

    sell = (

    (data["EMA20"] < data["EMA50"]) &

    (data["MACD"] < data["MACD_SIGNAL"]) &

    (data["RSI"] <= 48) &

    (data["ADX"] >= adx_min)

    )

    data["Signal"] = "HOLD"
    
    data["BUY_ENTRY"] = buy & (~buy.shift(1).fillna(False))
    data["SELL_ENTRY"] = sell & (~sell.shift(1).fillna(False))

    data.loc[buy, "Signal"] = "BUY"
    data.loc[sell, "Signal"] = "SELL"

    buy_signal = buy & (~buy.shift(1, fill_value=False))
    sell_signal = sell & (~sell.shift(1, fill_value=False))

    data["BUY_MARKER"] = buy_signal

    data["SELL_MARKER"] = sell_signal

    print(data[["Signal", "BUY_MARKER", "SELL_MARKER"]].tail(20))

    print("BUY =", buy.sum())
    print("SELL =", sell.sum())

    print(data[
        [
            "EMA20",
            "EMA50",
            "MACD",
            "MACD_SIGNAL",
            "RSI",
            "ADX",
            "AI_SCORE",
            "CONFIDENCE",
            "HTF_BULLISH"
        ]
    ].tail(10))

    return data