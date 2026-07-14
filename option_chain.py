import upstox_client
from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)

options_api = upstox_client.OptionsApi(api_client)


def get_option_chain():

    response = options_api.get_put_call_option_chain(
        instrument_key="NSE_INDEX|Nifty 50"
    )

    return response

import pandas as pd

def get_option_contracts():

    response = options_api.get_option_contracts(
        instrument_key="NSE_INDEX|Nifty 50"
    )

    contracts = pd.DataFrame([vars(x) for x in response.data])

    contracts.columns = contracts.columns.str.lstrip("_")

    print(type(contracts))
    print(contracts.columns)

    return contracts