from data import get_nifty_data
from indicators import add_indicators
from strategy import generate_signal

from option_history import get_option_history_df
from signal_mapper import map_signal_to_option


def run_option_backtest():

    # NIFTY Data
    data, close = get_nifty_data()

    data = add_indicators(data)

    data = generate_signal(data, close)

    # BUY Signals
    signals = data[data["Signal"] == "BUY"].reset_index()

    print("BUY Signals :", len(signals))

    # ATM Option History
    option_df = get_option_history_df("NSE_FO|57338")

    print("Option Candles :", len(option_df))

    # Map Signals
    mapped = map_signal_to_option(signals, option_df)

    print("Mapped Trades :", len(mapped))

    print(mapped.head())

    if len(mapped) == 0:
        print("No trades found.")
        return

    trade = mapped.iloc[0]

    print("\nFirst Trade")
    print(trade)

    entry_time = trade["Datetime"]
    entry_price = trade["Premium"]

    print("\nEntry Time :", entry_time)
    print("Entry Price:", entry_price)

    future = option_df[
    option_df["Datetime"] > entry_time
]

    print("\nFuture Candles :", len(future))

    print(future.head())


if __name__ == "__main__":
    run_option_backtest()