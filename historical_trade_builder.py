from historical_spot_data import get_historical_spot_data
from indicators import add_indicators
from strategy import generate_signal
from historical_contract_resolver import load_contracts, resolve_option_contract


def build_historical_trades(
    from_date,
    to_date,
):

    print("Loading historical spot data...")

    data = get_historical_spot_data(
        from_date=from_date,
        to_date=to_date,
        interval="5m"
    )

    print("Spot Candles :", len(data))

    print("Adding indicators...")

    data = add_indicators(data)

    print("Indicators added.")

    print(data.columns.tolist())

    print()

    print("Generating signals...")

    data = generate_signal(
        data,
        data["Close"]
    )

    buy_entries = data[data["BUY_ENTRY"]].copy()
    sell_entries = data[data["SELL_ENTRY"]].copy()

    print()
    print("Loading option contracts...")
    contracts_df = load_contracts("option_contracts.csv")

    print()
    print("BUY Entries :", len(buy_entries))
    print("SELL Entries:", len(sell_entries))

    print()
    print(buy_entries[["Datetime", "Close"]].head())

    print()
    print(sell_entries[["Datetime", "Close"]].head())

    print("Signals generated.")

    print()

    print("BUY Signals :", data["BUY_ENTRY"].sum())
    print("SELL Signals:", data["SELL_ENTRY"].sum())

    selected_buy_entries = buy_entries.head(5)
    resolved_signals = 0

    for _, signal in selected_buy_entries.iterrows():
        signal_time = signal["Datetime"]
        spot_price = signal["Close"]

        try:
            contract = resolve_option_contract(
                signal_datetime=signal_time,
                spot_price=spot_price,
                signal_side="BUY_ENTRY",
                contracts_df=contracts_df,
            )
        except (TypeError, ValueError) as error:
            print("--------------------------------")
            print("Signal Time :", signal_time)
            print("Spot :", spot_price)
            print("Could not resolve contract:", error)
            print("--------------------------------")
            continue

        resolved_signals += 1
        print("--------------------------------")
        print("Signal Time :", signal_time)
        print("Spot :", spot_price)
        print("Expiry :", contract["expiry"])
        print("Strike :", contract["strike_price"])
        print("Option Type :", contract["instrument_type"])
        print("Trading Symbol :", contract["trading_symbol"])
        print("Instrument Key :", contract["instrument_key"])
        print("Lot Size :", contract["lot_size"])
        print("--------------------------------")

    print(f"Resolved {resolved_signals} / {len(selected_buy_entries)} signals.")


if __name__ == "__main__":

    build_historical_trades(
        from_date="2026-07-01",
        to_date="2026-07-10",
    )
