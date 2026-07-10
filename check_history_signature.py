import inspect
import upstox_client

print(inspect.signature(
    upstox_client.HistoryV3Api.get_historical_candle_data
))