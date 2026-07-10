from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from expiry_calendar import get_weekly_expiry


VALID_SIGNAL_SIDES = {"BUY_ENTRY", "SELL_ENTRY"}
OPTION_TYPE_BY_SIGNAL = {
    "BUY_ENTRY": "CE",
    "SELL_ENTRY": "PE",
}


def _get_atm_strike(spot_price: float) -> int:
    if spot_price <= 0:
        raise ValueError("spot_price must be greater than zero.")

    return int(round(spot_price / 50) * 50)


def _normalize_expiry(value: Any) -> date:
    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        raise ValueError(f"Invalid expiry value found in contracts_df: {value!r}")

    return parsed.date()


def _get_option_type_column(contracts_df: pd.DataFrame) -> str:
    if "option_type" in contracts_df.columns:
        return "option_type"

    if "instrument_type" in contracts_df.columns:
        return "instrument_type"

    raise ValueError(
        "contracts_df must contain an option type column named "
        "'option_type' or 'instrument_type'."
    )


def _require_columns(contracts_df: pd.DataFrame) -> None:
    option_type_column = _get_option_type_column(contracts_df)
    required_columns = [
        "instrument_key",
        "trading_symbol",
        "expiry",
        "strike_price",
        option_type_column,
        "lot_size",
    ]
    missing = [column for column in required_columns if column not in contracts_df.columns]

    if missing:
        raise ValueError(
            "contracts_df is missing required columns: " + ", ".join(missing)
        )


def resolve_option_contract(
    signal_datetime: datetime,
    spot_price: float,
    signal_side: str,
    contracts_df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Resolve the historical NIFTY option contract for a signal.

    The selected contract is based on the signal timestamp, historical spot
    price, signal side, nearest 50-point ATM strike, and weekly expiry from
    expiry_calendar.get_weekly_expiry().

    Args:
        signal_datetime: Timezone-aware signal datetime.
        spot_price: Historical NIFTY spot price at the signal timestamp.
        signal_side: "BUY_ENTRY" for CE or "SELL_ENTRY" for PE.
        contracts_df: DataFrame of Upstox option contracts. Required columns:
            instrument_key, trading_symbol, expiry, strike_price, option_type
            or instrument_type, and lot_size.

    Returns:
        A dictionary containing instrument_key, trading_symbol, expiry, strike,
        option_type, and lot_size.

    Raises:
        ValueError: If the signal side is invalid, the contract DataFrame is
            empty, required columns are missing, or no matching contract exists.

    Examples:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> contracts = pd.DataFrame([{
        ...     "instrument_key": "NSE_FO|1",
        ...     "trading_symbol": "NIFTY2670924400CE",
        ...     "expiry": "2026-07-09",
        ...     "strike_price": 24400,
        ...     "option_type": "CE",
        ...     "lot_size": 75,
        ... }])
        >>> resolve_option_contract(
        ...     datetime(2026, 7, 6, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
        ...     24383,
        ...     "BUY_ENTRY",
        ...     contracts,
        ... )["option_type"]
        'CE'
    """
    if signal_side not in VALID_SIGNAL_SIDES:
        raise ValueError(
            "Invalid signal_side. Expected 'BUY_ENTRY' or 'SELL_ENTRY', "
            f"got {signal_side!r}."
        )

    if contracts_df is None or contracts_df.empty:
        raise ValueError("contracts_df is empty. Cannot resolve option contract.")

    _require_columns(contracts_df)

    expiry = get_weekly_expiry(signal_datetime)
    strike = _get_atm_strike(float(spot_price))
    option_type = OPTION_TYPE_BY_SIGNAL[signal_side]
    option_type_column = _get_option_type_column(contracts_df)

    contracts = contracts_df.copy()
    contracts["_normalized_expiry"] = contracts["expiry"].apply(_normalize_expiry)
    contracts["_normalized_strike"] = pd.to_numeric(
        contracts["strike_price"],
        errors="coerce",
    )
    contracts["_normalized_option_type"] = (
        contracts[option_type_column].astype(str).str.upper().str.strip()
    )

    matches = contracts[
        (contracts["_normalized_expiry"] == expiry)
        & (contracts["_normalized_strike"] == strike)
        & (contracts["_normalized_option_type"] == option_type)
    ].sort_values("_normalized_expiry")

    if matches.empty:
        raise ValueError(
            "Option contract not found for "
            f"signal_datetime={signal_datetime}, spot_price={spot_price}, "
            f"signal_side={signal_side}, expiry={expiry}, strike={strike}, "
            f"option_type={option_type}."
        )

    selected = matches.iloc[0]

    return {
        "instrument_key": selected["instrument_key"],
        "trading_symbol": selected["trading_symbol"],
        "expiry": selected["_normalized_expiry"],
        "strike": int(selected["_normalized_strike"]),
        "option_type": selected["_normalized_option_type"],
        "lot_size": int(selected["lot_size"]),
    }


if __name__ == "__main__":
    from zoneinfo import ZoneInfo

    demo_contracts = pd.DataFrame(
        [
            {
                "instrument_key": "NSE_FO|CE24400",
                "trading_symbol": "NIFTY2670924400CE",
                "expiry": "2026-07-09",
                "strike_price": 24400,
                "option_type": "CE",
                "lot_size": 75,
            },
            {
                "instrument_key": "NSE_FO|PE24300",
                "trading_symbol": "NIFTY2670924300PE",
                "expiry": "2026-07-09",
                "strike_price": 24300,
                "option_type": "PE",
                "lot_size": 75,
            },
        ]
    )

    buy_contract = resolve_option_contract(
        signal_datetime=datetime(2026, 7, 6, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
        spot_price=24383,
        signal_side="BUY_ENTRY",
        contracts_df=demo_contracts,
    )
    sell_contract = resolve_option_contract(
        signal_datetime=datetime(2026, 7, 6, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
        spot_price=24324,
        signal_side="SELL_ENTRY",
        contracts_df=demo_contracts,
    )

    print("BUY_ENTRY contract")
    print(buy_contract)
    print("\nSELL_ENTRY contract")
    print(sell_contract)
