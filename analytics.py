import pandas as pd

df = pd.read_csv("trade_history.csv")

print("\n========== TRADE ANALYTICS ==========\n")

# Basic Stats
print(f"Total Trades : {len(df)}")
print(f"Wins         : {(df['Result']=='WIN').sum()}")
print(f"Losses       : {(df['Result']=='LOSS').sum()}")

print("\nAverage Profit")
print(df["Profit"].mean())

print("\nBest Trade")
print(df["Profit"].max())

print("\nWorst Trade")
print(df["Profit"].min())

print("\nAverage AI Score")

print(df.groupby("Result")["AI_SCORE"].mean())

print("\nAverage RSI")

print(df.groupby("Result")["RSI"].mean())

print("\nAverage ADX")

print(df.groupby("Result")["ADX"].mean())

print("\n========== AI SCORE BUCKETS ==========\n")

bins = [0, 60, 70, 80, 90, 100]
labels = ["0-60", "60-70", "70-80", "80-90", "90-100"]

df["AI_BUCKET"] = pd.cut(
    df["AI_SCORE"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

print(
    df.groupby("AI_BUCKET")["Profit"].agg(
        ["count", "mean", "sum"]
    )
)

print("\n========== RSI BUCKETS ==========\n")

rsi_bins = [0, 50, 60, 70, 80, 100]
rsi_labels = ["0-50", "50-60", "60-70", "70-80", "80-100"]

df["RSI_BUCKET"] = pd.cut(
    df["RSI"],
    bins=rsi_bins,
    labels=rsi_labels,
    include_lowest=True
)

print(
    df.groupby("RSI_BUCKET")["Profit"].agg(
        ["count", "mean", "sum"]
    )
)

print("\n========== ADX BUCKETS ==========\n")

adx_bins = [0, 20, 30, 40, 50, 100]
adx_labels = ["0-20", "20-30", "30-40", "40-50", "50+"]

df["ADX_BUCKET"] = pd.cut(
    df["ADX"],
    bins=adx_bins,
    labels=adx_labels,
    include_lowest=True
)

print(
    df.groupby("ADX_BUCKET")["Profit"].agg(
        ["count", "mean", "sum"]
    )
)