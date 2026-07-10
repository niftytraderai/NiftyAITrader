from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Union

import pandas as pd
import yfinance as yf


DateLike = Union[str, date, datetime]


def _normalize_start_date(value: DateLike) -> datetime:
    parsed = pd.to_datetime(value)

    if pd.isna(parsed):
        raise ValueError("from_date must be a valid date or datetime.")

    return parsed.to_pydatetime()


def _normalize_end_date(value: DateLike) -> datetime:
    parsed = pd.to_datetime(value)

    if pd.isna(parsed):
        raise ValueError("to_date must be a valid date or datetime.")

    end = parsed.to_pydatetime()

    if isinstance(value, str) and len(value.strip()) <= 10:
        return datetime.combine(end.date() + timedelta(days=1), time.min)

    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value + timedelta(days=1), time.min)

    return end


def get_historical_spot_data(
    from_date: DateLike,
    to_date: DateLike,
    interval: str = "5m",
) -> pd.DataFrame:
    """
    Fetch historical NIFTY spot candles from Yahoo Finance.

    Args:
        from_date: Start date or datetime accepted by pandas.to_datetime.
        to_date: End date or datetime accepted by pandas.to_datetime. Date-only
            values are treated as inclusive for the full trading day.
        interval: Yahoo Finance candle interval, such as "1m", "5m", "15m",
            "30m", "60m", or "1d".

    Returns:
        A clean DataFrame with timezone-aware Asia/Kolkata Datetime values and
        only these columns: Datetime, Open, High, Low, Close, Volume.

    Raises:
        ValueError: If dates are invalid, the range is invalid, or Yahoo returns
            no candles.
        RuntimeError: If Yahoo Finance cannot be reached or returns malformed
            candle data.
    """
    start = _normalize_start_date(from_date)
    end = _normalize_end_date(to_date)

    if start >= end:
        raise ValueError("from_date must be earlier than to_date.")

    try:
        raw = yf.Ticker("^NSEI").history(
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch NIFTY spot data: {exc}") from exc

    if raw is None or raw.empty:
        raise ValueError(
            "Yahoo Finance returned no NIFTY spot candles for the requested "
            f"range: {from_date} to {to_date}, interval={interval}."
        )

    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required_columns if column not in raw.columns]

    if missing:
        raise RuntimeError(
            "Yahoo Finance response is missing required columns: "
            + ", ".join(missing)
        )

    data = raw.reset_index()
    datetime_column = "Datetime" if "Datetime" in data.columns else "Date"
    data = data.rename(columns={datetime_column: "Datetime"})

    data["Datetime"] = pd.to_datetime(data["Datetime"])

    if data["Datetime"].dt.tz is None:
        data["Datetime"] = data["Datetime"].dt.tz_localize("Asia/Kolkata")
    else:
        data["Datetime"] = data["Datetime"].dt.tz_convert("Asia/Kolkata")

    data = data[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
    data = data.dropna(subset=["Datetime", "Open", "High", "Low", "Close"])
    data = data.drop_duplicates(subset=["Datetime"], keep="last")
    data = data.sort_values("Datetime").reset_index(drop=True)

    if data.empty:
        raise ValueError(
            "No valid NIFTY spot candles remained after cleaning Yahoo Finance "
            "data."
        )

    return data


if __name__ == "__main__":
    candles = get_historical_spot_data(
        from_date=date.today() - timedelta(days=5),
        to_date=date.today(),
    )

    print("Number of candles:", len(candles))
    print("\nFirst 5 rows")
    print(candles.head())
    print("\nLast 5 rows")
    print(candles.tail())
