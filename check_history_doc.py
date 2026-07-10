import inspect
import upstox_client

print(inspect.getfullargspec(
    upstox_client.HistoryV3Api.get_historical_candle_data
))

print("\n====================\n")

print(upstox_client.HistoryV3Api.get_historical_candle_data.__doc__)