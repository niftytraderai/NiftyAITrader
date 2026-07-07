import pandas as pd

def optimize():

    try:
        df = pd.read_csv("trade_history.csv")
    except:
        print("trade_history.csv not found.")
        return

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

        print(f"\n{c}")

        print("Winner Avg :", round(winners[c].mean(),2))
        print("Loser Avg  :", round(losers[c].mean(),2))

    print("\n========== SUGGESTED SETTINGS ==========\n")

    ai = round(winners["AI_SCORE"].mean(),2)
    rsi = round(winners["RSI"].mean(),2)
    adx = round(winners["ADX"].mean(),2)

    print(f"Minimum AI Score : {ai}")
    print(f"Minimum RSI      : {rsi}")
    print(f"Minimum ADX      : {adx}")

if __name__ == "__main__":
    optimize()