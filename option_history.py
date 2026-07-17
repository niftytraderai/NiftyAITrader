import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)
history_api = upstox_client.HistoryApi(api_client)


# ===========================
# LIVE OPTION DATA
# ===========================

def get_live_option_data(
    instrument_key,
    interval="1minute"
):

    response = history_api.get_intra_day_candle_data(
        instrument_key=instrument_key,
        interval=interval,
        api_version="2.0"
    )

    candles = response.data.candles

    if not candles:
        return pd.DataFrame(columns=[
            "Datetime","Open","High","Low","Close","Volume","OI"
        ])

    df = pd.DataFrame(
        candles,
        columns=[
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "OI"
        ]
    )

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.sort_values("Datetime")
    df.reset_index(drop=True, inplace=True)

    return df


# ===========================
# HISTORICAL OPTION DATA
# ===========================

def get_option_history_df(
    instrument_key,
    from_date,
    to_date,
    interval="1minute"
):

    print("=" * 60)
    print("Instrument :", instrument_key)
    print("From       :", from_date)
    print("To         :", to_date)
    print("Interval   :", interval)
    print("=" * 60)

    response = history_api.get_historical_candle_data1(
        instrument_key=instrument_key,
        interval=interval,
        to_date=to_date,
        from_date=from_date,
        api_version="2.0"
    )

    candles = response.data.candles

    if not candles:
        return pd.DataFrame(columns=[
            "Datetime","Open","High","Low","Close","Volume","OI"
        ])

    df = pd.DataFrame(
        candles,
        columns=[
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "OI"
        ]
    )

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.sort_values("Datetime")
    df.reset_index(drop=True, inplace=True)

    return df