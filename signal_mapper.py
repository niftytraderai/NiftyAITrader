import pandas as pd


def map_signal_to_option(signal_df, option_df):
    """
    AI Signal ko Option Premium se map karta hai.
    """

    signal_df = signal_df.copy()
    option_df = option_df.copy()

    signal_df["Datetime"] = pd.to_datetime(signal_df["Datetime"])
    option_df["Datetime"] = pd.to_datetime(option_df["Datetime"])

    option_df = option_df.set_index("Datetime")

    entries = []

    for _, row in signal_df.iterrows():

        if row["Signal"] != "BUY":
            continue

        time = row["Datetime"]

        if time in option_df.index:

            premium = option_df.loc[time]["Close"]

            entries.append({

                "Datetime": time,

                "Spot": row["Close"],

                "Premium": premium

            })

    return pd.DataFrame(entries)