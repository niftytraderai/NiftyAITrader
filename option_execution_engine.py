"""Deterministic execution simulation for historical option candles."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Union

import pandas as pd
from option_costs import calculate_trade_cost


DateTimeLike = Union[str, datetime, pd.Timestamp]

MAX_HOLD_DAYS = 5

REQUIRED_COLUMNS = {
    "Datetime",
    "Open",
    "High",
    "Low",
    "Close"
}


def _prepare_candles(option_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and return chronologically sorted candles with a Datetime column."""
    if not isinstance(option_df, pd.DataFrame):
        raise TypeError("option_df must be a pandas DataFrame.")
    if option_df.empty:
        raise ValueError("option_df is empty; no option candles are available.")

    missing_columns = REQUIRED_COLUMNS - set(option_df.columns)
    if missing_columns:
        raise ValueError(
            "option_df is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    candles = option_df.copy()
    if "Datetime" not in candles.columns:
        if not isinstance(candles.index, pd.DatetimeIndex):
            raise ValueError(
                "option_df must contain a 'Datetime' column or use a DatetimeIndex."
            )
        candles = candles.reset_index().rename(columns={candles.index.name or "index": "Datetime"})

    candles["Datetime"] = pd.to_datetime(candles["Datetime"], errors="coerce")

    print(candles[["Open", "High", "Low", "Close"]].head(10))
    print(candles[["Open", "High", "Low", "Close"]].dtypes)
    if candles["Datetime"].isna().any():
        raise ValueError("option_df contains invalid Datetime values.")

    for column in ["Open", "High", "Low", "Close"]:
        candles[column] = pd.to_numeric(candles[column], errors="coerce")
    if candles[["Open", "High", "Low", "Close"]].isna().any().any():
        raise ValueError("option_df contains non-numeric Close, High, or Low values.")

    print(candles.dtypes)
    print(type(candles["Datetime"].iloc[0]))
    print(candles["Datetime"].head())    

    return candles.sort_values("Datetime").reset_index(drop=True)


def _align_entry_time(entry_time: DateTimeLike, candle_times: pd.Series) -> pd.Timestamp:
    """Parse an entry time and align it with the candle timestamp timezone."""
    entry_timestamp = pd.to_datetime(entry_time, errors="coerce")
    if pd.isna(entry_timestamp):
        raise ValueError(f"entry_time is invalid: {entry_time!r}")

    print(type(candle_times))
    print(candle_times.dtype)
    print(candle_times.head())   

    candle_timezone = candle_times.dt.tz
    if candle_timezone is not None and entry_timestamp.tzinfo is None:
        return entry_timestamp.tz_localize(candle_timezone)
    if candle_timezone is None and entry_timestamp.tzinfo is not None:
        return entry_timestamp.tz_convert(None)
    return entry_timestamp


def simulate_option_trade(
    option_df: pd.DataFrame,
    entry_time: DateTimeLike,
    stop_loss_pct: float = 30,
    target_pct: float = 50,
    quantity = 75,
) -> dict[str, Any]:
    """Simulate one long option trade using OHLC candles.

    The first candle at or after ``entry_time`` supplies the entry close. Each
    candle from that point is examined for a stop-loss or target touch using
    its Low and High. If both occur in one candle, the stop loss is selected
    conservatively because intrabar order is not available from OHLC data.

    Args:
        option_df: Candle data with Datetime, Close, High, and Low columns.
        entry_time: Desired entry timestamp.
        stop_loss_pct: Percentage below entry price for the stop loss.
        target_pct: Percentage above entry price for the target.

    Returns:
        Entry/exit details, P&L, percentage return, and the exit reason.

    Raises:
        TypeError: If inputs have unsupported types.
        ValueError: If candle data or trade parameters are invalid, or no
            candle exists at or after the requested entry time.
    """
    if not isinstance(stop_loss_pct, (int, float)) or not isinstance(target_pct, (int, float)):
        raise TypeError("stop_loss_pct and target_pct must be numeric.")
    if not 0 <= stop_loss_pct < 100:
        raise ValueError("stop_loss_pct must be at least 0 and less than 100.")
    if target_pct < 0:
        raise ValueError("target_pct must be at least 0.")

    candles = _prepare_candles(option_df)
    entry_timestamp = _align_entry_time(entry_time, candles["Datetime"])
    print("Signal:", entry_timestamp)
    print("Last Candle:", candles["Datetime"].iloc[-1])
    future_candles = candles[candles["Datetime"] >= entry_timestamp]
    entry_date = entry_timestamp.date()
    if future_candles.empty:
        raise ValueError(
            f"No option candle exists at or after entry_time={entry_timestamp}."
        )

    entry_candle = future_candles.iloc[0]
    entry_price = float(entry_candle["Close"])
    if entry_price <= 0:
        raise ValueError("Entry candle Close must be greater than zero.")

    entry_date = entry_candle["Datetime"].date()    

    stop_loss = entry_price * (1 - stop_loss_pct / 100)
    target = entry_price * (1 + target_pct / 100)
    exit_candle = future_candles.iloc[-1]
    exit_price = float(exit_candle["Close"])
    exit_reason = "END_OF_DATA"

    for _, candle in future_candles.iterrows():
        current_date = candle["Datetime"].date()

        if current_date > entry_date:

            open_price = float(candle["Open"])

            if open_price <= stop_loss:
                exit_candle = candle
                exit_price = open_price
                exit_reason = "GAP_STOP"
                break

            if open_price >= target:
                exit_candle = candle
                exit_price = open_price
                exit_reason = "GAP_TARGET"
                break    
        if float(candle["Low"]) <= stop_loss:
            exit_candle = candle
            exit_price = stop_loss
            exit_reason = "STOP_LOSS"
            break
        if float(candle["High"]) >= target:
            exit_candle = candle
            exit_price = target
            exit_reason = "TARGET"
            break
        days_held = (current_date - entry_date).days

        if days_held >= MAX_HOLD_DAYS:
            exit_candle = candle
            exit_price = float(candle["Open"])
            exit_reason = "MAX_HOLD"
            break    

    gross_pnl = (exit_price - entry_price) * quantity

    costs = calculate_trade_cost(
        entry_price=entry_price,
        exit_price=exit_price,
        quantity=quantity
    )

    net_pnl = gross_pnl - costs["total_cost"]

    return {
        "entry_time": entry_candle["Datetime"],
        "exit_time": exit_candle["Datetime"],
        "entry_price": entry_price,
        "exit_price": exit_price,

        "quantity": quantity,

        "gross_pnl": gross_pnl,
        "brokerage": costs["brokerage"],
        "slippage": costs["slippage"],
        "other_charges": costs["other_charges"],
        "net_pnl": net_pnl,

        "pnl": net_pnl,

        "return_pct": (net_pnl / (entry_price * quantity)) * 100,

        "exit_reason": exit_reason,
    }


if __name__ == "__main__":
    example_candles = pd.DataFrame(
        {
            "Datetime": pd.to_datetime([
                "2026-07-09 09:15:00",
                "2026-07-09 09:16:00",
                "2026-07-09 09:17:00",
            ]),
            "Close": [100.0, 110.0, 145.0],
            "High": [105.0, 120.0, 152.0],
            "Low": [98.0, 107.0, 140.0],
        }
    )
    print(simulate_option_trade(example_candles, "2026-07-09 09:15:00"))
