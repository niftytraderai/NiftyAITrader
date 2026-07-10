# inspect_history.py

import inspect
import upstox_client

print(inspect.getsource(
    upstox_client.HistoryV3Api.get_historical_candle_data_with_http_info
))