import upstox_client
from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)
market_api = upstox_client.MarketQuoteV3Api(api_client)


def get_live_price():

    response = market_api.get_ltp(
        instrument_key="NSE_INDEX|Nifty 50"
    )

    return response.data["NSE_INDEX:Nifty 50"].last_price