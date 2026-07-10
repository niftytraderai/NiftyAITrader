from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Iterable, Optional
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")
DEFAULT_EXPIRY_WEEKDAY = 3
DEFAULT_EXPIRY_CUTOFF = time(hour=15, minute=15)


def _ensure_ist(signal_datetime: datetime) -> datetime:
    if signal_datetime.tzinfo is None:
        raise ValueError("signal_datetime must be timezone-aware.")

    return signal_datetime.astimezone(IST)


def _normalize_holiday_expiries(
    holiday_adjusted_expiries: Optional[Iterable[date]] = None,
) -> set[date]:
    if holiday_adjusted_expiries is None:
        return set()

    return set(holiday_adjusted_expiries)


def _default_weekly_expiry(candidate_date: date) -> date:
    days_until_expiry = (DEFAULT_EXPIRY_WEEKDAY - candidate_date.weekday()) % 7
    return candidate_date + timedelta(days=days_until_expiry)


def _resolve_weekly_expiry(
    candidate_date: date,
    holiday_adjusted_expiries: Optional[Iterable[date]] = None,
) -> date:
    """
    Resolve the weekly expiry for a candidate date.

    This currently uses the standard Thursday NIFTY weekly expiry. The optional
    holiday_adjusted_expiries argument keeps the lookup replaceable with a CSV
    backed exchange calendar later.
    """
    adjusted_expiries = _normalize_holiday_expiries(holiday_adjusted_expiries)

    if adjusted_expiries:
        valid_expiries = sorted(expiry for expiry in adjusted_expiries if expiry >= candidate_date)

        if valid_expiries:
            return valid_expiries[0]

    return _default_weekly_expiry(candidate_date)


def is_expiry_day(signal_datetime: datetime) -> bool:
    """
    Return True when signal_datetime falls on the selected weekly expiry date.

    Args:
        signal_datetime: A timezone-aware datetime. It is converted to
            Asia/Kolkata before evaluation.

    Returns:
        True if the signal date is the current weekly expiry date, otherwise
        False.

    Example:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> is_expiry_day(datetime(2026, 7, 9, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")))
        True
    """
    signal_ist = _ensure_ist(signal_datetime)
    return signal_ist.date() == _resolve_weekly_expiry(signal_ist.date())


def is_after_expiry_cutoff(signal_datetime: datetime) -> bool:
    """
    Return True when signal_datetime is after the Thursday 15:15 IST cutoff.

    Args:
        signal_datetime: A timezone-aware datetime. It is converted to
            Asia/Kolkata before evaluation.

    Returns:
        True only on expiry day after or at the default 15:15 IST cutoff.

    Example:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> is_after_expiry_cutoff(datetime(2026, 7, 9, 15, 20, tzinfo=ZoneInfo("Asia/Kolkata")))
        True
    """
    signal_ist = _ensure_ist(signal_datetime)

    if not is_expiry_day(signal_ist):
        return False

    return signal_ist.time() >= DEFAULT_EXPIRY_CUTOFF


def get_weekly_expiry(signal_datetime: datetime) -> date:
    """
    Get the correct weekly NIFTY expiry date for a signal timestamp.

    Rules:
        - Before the weekly expiry cutoff, return the current weekly expiry.
        - On expiry day after the cutoff, return the next weekly expiry.
        - After expiry day, return the next weekly expiry.

    Args:
        signal_datetime: A timezone-aware datetime. It is converted to
            Asia/Kolkata before expiry selection.

    Returns:
        The selected weekly expiry date.

    Raises:
        ValueError: If signal_datetime is timezone-naive.

    Examples:
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> get_weekly_expiry(datetime(2026, 7, 6, 10, 0, tzinfo=ZoneInfo("Asia/Kolkata")))
        datetime.date(2026, 7, 9)
        >>> get_weekly_expiry(datetime(2026, 7, 9, 15, 20, tzinfo=ZoneInfo("Asia/Kolkata")))
        datetime.date(2026, 7, 16)
    """
    signal_ist = _ensure_ist(signal_datetime)
    current_expiry = _resolve_weekly_expiry(signal_ist.date())

    if signal_ist.date() > current_expiry:
        return _resolve_weekly_expiry(signal_ist.date())

    if signal_ist.date() == current_expiry and is_after_expiry_cutoff(signal_ist):
        return _resolve_weekly_expiry(current_expiry + timedelta(days=1))

    return current_expiry


if __name__ == "__main__":
    examples = {
        "Monday": datetime(2026, 7, 6, 10, 0, tzinfo=IST),
        "Wednesday": datetime(2026, 7, 8, 10, 0, tzinfo=IST),
        "Thursday morning": datetime(2026, 7, 9, 10, 0, tzinfo=IST),
        "Thursday after cutoff": datetime(2026, 7, 9, 15, 20, tzinfo=IST),
        "Friday": datetime(2026, 7, 10, 10, 0, tzinfo=IST),
    }

    for label, example_datetime in examples.items():
        print(f"{label}: {example_datetime} -> {get_weekly_expiry(example_datetime)}")
