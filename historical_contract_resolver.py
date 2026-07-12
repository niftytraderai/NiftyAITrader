from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from expiry_calendar import get_weekly_expiry


VALID_SIGNAL_SIDES = {"BUY_ENTRY", "SELL_ENTRY"}
INSTRUMENT_TYPE_BY_SIGNAL = {
    "BUY_ENTRY": "CE",
    "SELL_ENTRY": "PE",
}


def load_contracts(csv_path: str = "option_contracts.csv") -> pd.DataFrame:
    """Load locally downloaded option contracts from a CSV file."""
    try:
        contracts_df = pd.read_csv(csv_path)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Contract CSV file was not found: {csv_path!r}. "
            "Run download_option_contracts.py first."
        ) from error
    except (OSError, pd.errors.ParserError) as error:
        raise ValueError(f"Could not load contract CSV {csv_path!r}: {error}") from error

    print("\n===== SAMPLE CONTRACTS =====")
    print(contracts_df[[
        "expiry",
        "strike_price",
        "instrument_type",
        "trading_symbol"
    ]].head(20))

    print("\nExpiry dtype:", contracts_df["expiry"].dtype)
    print("Strike dtype:", contracts_df["strike_price"].dtype)

    print("\nUnique instrument types:")
    print(sorted(contracts_df["instrument_type"].dropna().unique()))

    if contracts_df.empty:
        raise ValueError(f"Contract CSV {csv_path!r} contains no contracts.")

    _require_columns(contracts_df)
    return contracts_df


def _get_atm_strike(spot_price: float) -> int:
    if spot_price <= 0:
        raise ValueError("spot_price must be greater than zero.")

    return int(round(spot_price / 50) * 50)


def _normalize_expiry(value: Any) -> date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Invalid expiry value found in contracts_df: {value!r}")
    return parsed.date()


def _require_columns(contracts_df: pd.DataFrame) -> None:
    required_columns = [
        "instrument_key",
        "trading_symbol",
        "expiry",
        "strike_price",
        "instrument_type",
        "lot_size",
    ]
    missing = [column for column in required_columns if column not in contracts_df.columns]
    if missing:
        raise ValueError("contracts_df is missing required columns: " + ", ".join(missing))


def resolve_option_contract(
    signal_datetime: datetime,
    spot_price: float,
    signal_side: str,
    contracts_df: pd.DataFrame,
) -> dict[str, Any]:
    """Resolve a contract exclusively from the locally loaded contracts DataFrame."""
    if signal_side not in VALID_SIGNAL_SIDES:
        raise ValueError(
            "Invalid signal_side. Expected 'BUY_ENTRY' or 'SELL_ENTRY', "
            f"got {signal_side!r}."
        )
    if not isinstance(contracts_df, pd.DataFrame):
        raise TypeError("contracts_df must be a pandas DataFrame loaded from the CSV.")
    if contracts_df.empty:
        raise ValueError("contracts_df is empty. Cannot resolve option contract.")

    _require_columns(contracts_df)

    expiry = get_weekly_expiry(
    signal_datetime,
    contracts_df=contracts_df
    )
    strike_price = _get_atm_strike(float(spot_price))
    instrument_type = INSTRUMENT_TYPE_BY_SIGNAL[signal_side]

    print(contracts_df["expiry"].head(10))
    print(contracts_df["instrument_type"].unique())
    print(contracts_df["strike_price"].head(20))
    print("Requested expiry:", expiry)
    print("Requested strike:", strike_price)
    print("Requested instrument_type:", instrument_type)

    contracts = contracts_df.copy()
    contracts["_normalized_expiry"] = contracts["expiry"].apply(_normalize_expiry)
    contracts["_normalized_strike_price"] = pd.to_numeric(
        contracts["strike_price"], errors="coerce"
    )
    contracts["_normalized_instrument_type"] = (
        contracts["instrument_type"].astype(str).str.upper().str.strip()
    )

    matches = contracts[
        (contracts["_normalized_expiry"] == expiry)
        & (contracts["_normalized_strike_price"] == strike_price)
        & (contracts["_normalized_instrument_type"] == instrument_type)
    ]

    if matches.empty:
        raise ValueError(
            "Option contract not found for "
            f"signal_datetime={signal_datetime}, spot_price={spot_price}, "
            f"signal_side={signal_side}, expiry={expiry}, "
            f"strike_price={strike_price}, instrument_type={instrument_type}."
        )

    selected = matches.iloc[0]
    return {
        "instrument_key": selected["instrument_key"],
        "trading_symbol": selected["trading_symbol"],
        "expiry": selected["_normalized_expiry"],
        "strike_price": int(selected["_normalized_strike_price"]),
        "instrument_type": selected["_normalized_instrument_type"],
        "lot_size": int(selected["lot_size"]),
    }


if __name__ == "__main__":
    from zoneinfo import ZoneInfo

    try:
        contracts = load_contracts()
        demo_rows = contracts.copy()
        demo_rows["_expiry"] = demo_rows["expiry"].apply(_normalize_expiry)
        demo_rows["_instrument_type"] = (
            demo_rows["instrument_type"].astype(str).str.upper().str.strip()
        )
        demo_rows["_strike_price"] = pd.to_numeric(
            demo_rows["strike_price"], errors="coerce"
        )
        demo_rows = demo_rows[
            (demo_rows["_instrument_type"] == "CE")
            & (demo_rows["_expiry"].apply(lambda value: value.weekday() == 3))
            & demo_rows["_strike_price"].notna()
        ].sort_values("_expiry")

        if demo_rows.empty:
            raise ValueError("No CE contracts with a Thursday expiry were found in the CSV.")

        demo_row = demo_rows.iloc[0]
        signal_datetime = datetime.combine(
            demo_row["_expiry"] - timedelta(days=3),
            datetime.min.time(),
            tzinfo=ZoneInfo("Asia/Kolkata"),
        ).replace(hour=10)
        selected_contract = resolve_option_contract(
            signal_datetime=signal_datetime,
            spot_price=float(demo_row["_strike_price"]),
            signal_side="BUY_ENTRY",
            contracts_df=contracts,
        )
        print("Selected BUY_ENTRY contract:")
        print(selected_contract)
    except (FileNotFoundError, TypeError, ValueError) as error:
        print(f"Could not resolve demo contract: {error}")
