import upstox_client
from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)

history_api = upstox_client.HistoryApi(api_client)


def get_option_history(instrument_key):

    response = history_api.get_historical_candle_data(
        instrument_key=instrument_key,
        interval="1minute",
        to_date="2026-07-09",
        api_version="2.0"
    )

    return response