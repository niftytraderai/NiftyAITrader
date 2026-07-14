import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)
history_api = upstox_client.HistoryApi(api_client)


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
        print("No candles returned from API")
        return pd.DataFrame(
            columns=[
                "Datetime",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "OI",
            ]
        )

    df = pd.DataFrame(
        candles,
        columns=[
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "OI",
        ]
    )

    df["Datetime"] = pd.to_datetime(df["Datetime"])

    df = df.sort_values("Datetime")

    df.reset_index(drop=True, inplace=True)

    return df