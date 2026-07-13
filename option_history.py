import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)
history_api = upstox_client.HistoryApi(api_client)


def get_option_history_df(
    instrument_key,
    from_date,
    to_date,
    interval="1minute"
):

    response = history_api.get_historical_candle_data1(
        instrument_key=instrument_key,
        interval=interval,
        to_date=to_date,
        from_date=from_date,
        api_version="2.0"
    )

    candles = response.data.candles

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

    print("Instrument :", instrument_key)
    print("From :", from_date)
    print("To   :", to_date)
    print("Candles :", len(df))

    return df