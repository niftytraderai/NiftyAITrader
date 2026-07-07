import pandas as pd


def optimize():

    df = pd.read_csv("trade_history.csv")

    if len(df) < 20:

        print("Need at least 20 trades.")

        return

    winners = df[df["Result"] == "WIN"]

    losers = df[df["Result"] == "LOSS"]

    print("\n========== AI OPTIMIZER ==========\n")

    cols = [

        "AI_SCORE",
        "RSI",
        "ADX",
        "ATR"

    ]

    for c in cols:

        w = winners[c].mean()

        l = losers[c].mean()

        print(c)

        print("Winner :", round(w,2))

        print("Loser  :", round(l,2))

        print("----------------------")

    print("\nSuggested Filters\n")

    print("Minimum AI Score :", round(winners["AI_SCORE"].mean(),2))

    print("Minimum ADX :", round(winners["ADX"].mean(),2))

    print("Best RSI :", round(winners["RSI"].mean(),2))