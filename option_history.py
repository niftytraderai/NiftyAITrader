import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN
from datetime import datetime

to_date = datetime.today().strftime("%Y-%m-%d")

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)

history_api = upstox_client.HistoryApi(api_client)


def get_option_history_df(instrument_key):

    response = history_api.get_historical_candle_data(
        instrument_key=instrument_key,
        interval="1minute",
        to_date=to_date,
        api_version="2.0"
    )

    candles = response.to_dict()["data"]["candles"]

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

    print("First Candle:", df["Datetime"].min())
    print("Last Candle :", df["Datetime"].max())

    return df