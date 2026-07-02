from datetime import datetime
from zoneinfo import ZoneInfo

def is_market_open():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    # Monday = 0, Sunday = 6
    if now.weekday() > 4:
        return False

    start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end = now.replace(hour=15, minute=30, second=0, microsecond=0)

    return start <= now <= end