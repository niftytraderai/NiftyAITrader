import pandas as pd


def get_historical_spot_data(
    from_date=None,
    to_date=None,
    interval=None,
):
    df = pd.read_csv("historical_spot.csv")

    df.columns = [c.lower() for c in df.columns]

    df.rename(columns={
        "datetime": "Datetime",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
        "oi": "OI",
    }, inplace=True)

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    print(df["Datetime"].dtype)
    print(df["Datetime"].head())

    df = df.sort_values("Datetime")
    df.reset_index(drop=True, inplace=True)

    if from_date is not None:
        from_date = pd.to_datetime(from_date).tz_localize("Asia/Kolkata")
        df = df[df["Datetime"] >= from_date]

    if to_date is not None:
        to_date = (
            pd.to_datetime(to_date)
            .tz_localize("Asia/Kolkata")
            + pd.Timedelta(days=1)
        )
        df = df[df["Datetime"] < to_date]

    print(f"Loaded {len(df)} spot candles from CSV.")

    return df