import pandas as pd
import upstox_client

from config_api import ACCESS_TOKEN

configuration = upstox_client.Configuration()
configuration.access_token = ACCESS_TOKEN

api_client = upstox_client.ApiClient(configuration)

history_api = upstox_client.HistoryApi(api_client)

from datetime import datetime, timedelta

def get_spot_history(from_date, to_date):

    print(f"Downloading {from_date} -> {to_date}")

    response = history_api.get_historical_candle_data1(
        instrument_key="NSE_INDEX|Nifty 50",
        interval="1minute",
        to_date=to_date,
        from_date=from_date,
        api_version="2.0"
    )

    return response

if __name__ == "__main__":

    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 7, 12)

    all_data = []

    current_date = start_date

    while current_date <= end_date:

        from_date = current_date.strftime("%Y-%m-%d")

        to_date = (current_date + timedelta(days=6)).strftime("%Y-%m-%d")

        print("=" * 50)

        response = get_spot_history(from_date, to_date)

        candles = response.data.candles

        all_data.extend(candles)

        print(f"Downloaded : {len(candles)} candles")

        current_date += timedelta(days=7)

        print("=" * 60)
        print(f"Total Candles : {len(all_data)}")

        df = pd.DataFrame(
            all_data,
            columns=[
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "oi",
            ],
        )

        # Datetime ko proper format me convert karo
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Oldest -> Newest
        df = df.sort_values("datetime")

        # Index reset
        df.reset_index(drop=True, inplace=True)

        # CSV Save
        df.to_csv("historical_spot.csv", index=False)

        print("CSV Saved Successfully ✅")
        print(df.head())
        print(df.tail())   