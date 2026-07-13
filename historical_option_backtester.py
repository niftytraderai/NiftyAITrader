"""Orchestrate historical option-contract resolution, data retrieval, and execution."""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path
from typing import Union

import pandas as pd

from historical_contract_resolver import load_contracts, resolve_option_contract
from historical_spot_data import get_historical_spot_data
from indicators import add_indicators
from option_data_cache import get_option_history_cached
from option_execution_engine import simulate_option_trade
from strategy import generate_signal


DateLike = Union[str, date, datetime]
LOGGER = logging.getLogger(__name__)
RESULT_COLUMNS = [
    "signal_time",
    "signal_side",
    "spot_price",

    "instrument_key",
    "trading_symbol",
    "expiry",
    "strike_price",
    "instrument_type",
    "lot_size",

    "entry_time",
    "exit_time",

    "entry_price",
    "exit_price",

    "quantity",

    "gross_pnl",
    "brokerage",
    "slippage",
    "other_charges",
    "net_pnl",

    "pnl",
    "return_pct",

    "exit_reason",

    "status",
    "error",
]


def run_historical_option_backtest(
    from_date: DateLike,
    to_date: DateLike,
    contracts_csv_path: Union[str, Path] = "option_contracts.csv",
    option_interval: str = "1minute",
    stop_loss_pct: float = 30,
    target_pct: float = 50,
    output_path: Union[str, Path] = "historical_option_trades.csv",
) -> pd.DataFrame:
    """Run a complete historical option backtest and write its trade report.

    Spot candles are used to generate both BUY_ENTRY and SELL_ENTRY signals.
    BUY entries resolve to calls and SELL entries resolve to puts through the
    contract resolver. Each option trade is simulated independently; a failed
    resolution, download, or simulation is recorded and does not stop later
    signals from being processed.

    Args:
        from_date: Inclusive start date for spot data.
        to_date: Inclusive end date for spot data and the option cache key.
        contracts_csv_path: Local option-contract CSV file.
        option_interval: Option-candle interval used in the cache key.
        stop_loss_pct: Stop loss percentage passed to the execution engine.
        target_pct: Target percentage passed to the execution engine.
        output_path: Destination CSV for completed and failed trade rows.

    Returns:
        A DataFrame containing one result row for every generated entry signal.

    Raises:
        RuntimeError: If initial spot-data preparation, contract loading, or
            report writing fails.
    """
    try:
        LOGGER.info("Loading historical spot data from %s to %s.", from_date, to_date)
        spot_data = get_historical_spot_data(from_date, to_date, interval="1minute")
        LOGGER.info("Adding indicators and generating signals.")
        signal_data = generate_signal(add_indicators(spot_data), spot_data["Close"])
        contracts_df = load_contracts(str(contracts_csv_path))
    except Exception as error:
        raise RuntimeError(f"Backtest setup failed: {error}") from error

    buy_entries = signal_data[signal_data["BUY_ENTRY"]].copy()
    buy_entries["signal_side"] = "BUY_ENTRY"
    sell_entries = signal_data[signal_data["SELL_ENTRY"]].copy()
    sell_entries["signal_side"] = "SELL_ENTRY"
    entries = pd.concat([buy_entries, sell_entries], ignore_index=True).sort_values("Datetime")
    total_signals = len(entries)
    resolved_contracts = 0
    completed_trades = 0
    failed_trades = 0
    results: list[dict[str, object]] = []

    LOGGER.info("Processing %d entry signals.", total_signals)
    
    for _, signal in entries.iterrows():
        signal_time = signal["Datetime"]
        signal_side = signal["signal_side"]
        spot_price = float(signal["Close"])

        print("=" * 70)
        print("Signal Time :", signal_time)
        print("Signal Side :", signal_side)
        print("Spot Price  :", spot_price)
        print("STEP 1")
        
        result_row: dict[str, object] = {
            "signal_time": signal_time,
            "signal_side": signal_side,
            "spot_price": spot_price,
            "status": "FAILED",
            "error": None,
        }

        try:
            contract = resolve_option_contract(
                signal_datetime=signal_time,
                spot_price=spot_price,
                signal_side=signal_side,
                contracts_df=contracts_df,
            )
            print("STEP 2")
            print(contract)
            resolved_contracts += 1

            option_history = get_option_history_cached(
                instrument_key=str(contract["instrument_key"]),
                from_date=pd.Timestamp(signal_time).date().isoformat(),
                to_date=to_date,
                interval=option_interval,
            )
            print("STEP 3")
            print(option_history.head())
            execution = simulate_option_trade(
                option_df=option_history,
                entry_time=signal_time,
                stop_loss_pct=stop_loss_pct,
                target_pct=target_pct,
                quantity=int(contract["lot_size"])
            )
            print("STEP 4")
            print(execution)

            result_row.update(contract)
            result_row.update(execution)
            result_row["status"] = "COMPLETED"
            completed_trades += 1
            LOGGER.info("Completed %s trade at %s.", signal_side, signal_time)
        except Exception as error:
            failed_trades += 1
            result_row["error"] = str(error)
            LOGGER.warning("Trade failed for %s at %s: %s", signal_side, signal_time, error)

        results.append(result_row)

    results_df = pd.DataFrame(results, columns=RESULT_COLUMNS)
    try:
        results_df.to_csv(output_path, index=False)
    except OSError as error:
        raise RuntimeError(f"Could not save backtest report {output_path!s}: {error}") from error

    net_pnl = pd.to_numeric(results_df["pnl"], errors="coerce").fillna(0).sum()
    print(f"Total Signals: {total_signals}")
    print(f"Resolved Contracts: {resolved_contracts}")
    print(f"Completed Trades: {completed_trades}")
    print(f"Failed Trades: {failed_trades}")
    print(f"Net PnL: {net_pnl:.2f}")
    return results_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run_historical_option_backtest(
            from_date="2026-02-01",
            to_date="2026-07-10",
        )
    except RuntimeError as error:
        LOGGER.error("Historical option backtest failed: %s", error)
