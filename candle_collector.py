import os
import pandas as pd


def save_spot_candle(data):

    folder = "market_data/spot"
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(
        folder,
        f"NIFTY_{pd.Timestamp.now().strftime('%Y_%m')}.csv"
    )

    latest = data.iloc[-1:].copy()

    if os.path.exists(filename):

        old = pd.read_csv(filename)

        last_saved = None

        if not old.empty:
            last_saved = str(old.iloc[-1]["datetime"])

        current = str(latest.index[-1])

        if last_saved == current:
            return

    latest.to_csv(
        filename,
        mode="a",
        index=True,
        header=not os.path.exists(filename)
    )