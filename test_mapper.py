from data import get_nifty_data
from indicators import add_indicators
from strategy import generate_signal
from option_history import get_option_history_df
from signal_mapper import map_signal_to_option

# NIFTY Data
data, close = get_nifty_data()

# Indicators
data = add_indicators(data)

print(data.columns.tolist())

data = generate_signal(data, close)

# BUY Signals
signals = data[data["Signal"] == "BUY"].reset_index()

# Option Premium
option_df = get_option_history_df("NSE_FO|57338")

mapped = map_signal_to_option(signals, option_df)

print(mapped.head())

print()

print("Total Entries =", len(mapped))