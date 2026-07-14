import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)
history_api = upstox_client.HistoryApi(api_client)


def get_live_spot_data():

    response = history_api.get_intra_day_candle_data(
        instrument_key="NSE_INDEX|Nifty 50",
        interval="1minute",
        api_version="2.0"
    )

    candles = response.data.candles

    df = pd.DataFrame(
        candles,
        columns=[
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "oi",
        ],
    )

    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.sort_values("datetime")

    df.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        },
        inplace=True,
    )

    df.set_index("datetime", inplace=True)

    return df