import inspect
import upstox_client

print(inspect.getsource(
    upstox_client.HistoryApi.get_historical_candle_data_with_http_info
))