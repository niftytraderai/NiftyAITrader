def generate_signal(data, close):

    data["Signal"] = "HOLD"

    buy = (
        (data["AI_SCORE"] >= 70) &
        (data["SUPERTREND_DIRECTION"] == True) &
        (data["MACD"] > data["MACD_SIGNAL"]) &
        (data["ADX"] >= 25)
    )

    sell = (
        (data["AI_SCORE"] <= 35)
    )

    data.loc[buy, "Signal"] = "BUY"
    data.loc[sell, "Signal"] = "SELL"

    return data