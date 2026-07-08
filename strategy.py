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

    data.loc[buy, "Signal"] = "BUY"
    data.loc[sell, "Signal"] = "SELL"

    return data