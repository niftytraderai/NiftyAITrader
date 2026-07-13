"""Local CSV cache for historical option-candle downloads."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
from typing import Union

import pandas as pd


DateLike = Union[str, date, datetime]
INVALID_FILENAME_CHARACTERS = re.compile(r'[<>:"/\\|?*]')


def _safe_filename_part(value: object) -> str:
    """Return a filesystem-safe representation of a cache-key value."""
    return INVALID_FILENAME_CHARACTERS.sub("_", str(value)).strip()


def get_option_history_cached(
    instrument_key: str,
    from_date: DateLike,
    to_date: DateLike,
    interval: str = "1minute",
) -> pd.DataFrame:
    """Return historical option data from a CSV cache or download it once.

    The cache filename includes the instrument, requested date range, and
    interval. The current ``option_history.get_option_history_df`` interface
    accepts an instrument key only, so the date range and interval are used to
    distinguish cached downloads.

    Args:
        instrument_key: Upstox option instrument key.
        from_date: Start date included in the cache key.
        to_date: End date included in the cache key.
        interval: Candle interval included in the cache key.

    Returns:
        Historical option candles as a pandas DataFrame.

    Raises:
        ValueError: If a required cache-key value is empty or data is invalid.
        RuntimeError: If option history cannot be downloaded or cached.
    """
    if not all(str(value).strip() for value in (instrument_key, from_date, to_date, interval)):
        raise ValueError("instrument_key, from_date, to_date, and interval are required.")

    cache_directory = Path("cache")
    try:
        cache_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise RuntimeError(f"Could not create cache directory {cache_directory!s}: {error}") from error

    filename = (
        f"{_safe_filename_part(instrument_key)}_"
        f"{_safe_filename_part(from_date)}_"
        f"{_safe_filename_part(to_date)}_"
        f"{_safe_filename_part(interval)}.csv"
    )
    cache_path = cache_directory / filename

    if cache_path.exists():
        try:
            dataframe = pd.read_csv(cache_path)
        except (OSError, pd.errors.ParserError) as error:
            raise RuntimeError(f"Could not read cached option history: {error}") from error

        print("Loaded option history from cache.")
        return dataframe

    try:
        from option_history import get_option_history_df

        dataframe = get_option_history_df(
            instrument_key=instrument_key,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )
    except Exception as error:
        raise RuntimeError(f"Could not download option history: {error}") from error

    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError("get_option_history_df() did not return a pandas DataFrame.")

    try:
        dataframe.to_csv(cache_path, index=False)
    except OSError as error:
        raise RuntimeError(f"Could not save option history cache: {error}") from error

    print("Downloaded option history and cached.")
    return dataframe


if __name__ == "__main__":
    try:
        demo_data = get_option_history_cached(
            instrument_key="NSE_FO|YOUR_OPTION_INSTRUMENT_KEY",
            from_date="2026-07-01",
            to_date="2026-07-09",
        )
        print(demo_data.head())
    except (RuntimeError, ValueError) as error:
        print(f"Option history cache demo failed: {error}")
