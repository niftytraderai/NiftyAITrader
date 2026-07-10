import inspect
import upstox_client

print(inspect.signature(
    upstox_client.HistoryApi.get_historical_candle_data
))