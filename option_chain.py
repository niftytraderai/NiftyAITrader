import requests
import pandas as pd


def get_option_chain():

    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json"
    }

    session = requests.Session()
   
    # Cookie generate
    session.get("https://www.nseindia.com", headers=headers)

    response = session.get(url, headers=headers)

    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print(response.text[:300])

   # data = response.json()

    return response.text

def get_summary():

    data = get_option_chain()

    records = data["records"]["data"]

    total_call_oi = 0
    total_put_oi = 0

    for row in records:

        if "CE" in row:
            total_call_oi += row["CE"]["openInterest"]

        if "PE" in row:
            total_put_oi += row["PE"]["openInterest"]

    pcr = total_put_oi / total_call_oi

    return {
        "CALL_OI": total_call_oi,
        "PUT_OI": total_put_oi,
        "PCR": round(pcr, 2)
    }

if __name__ == "__main__":

    result = get_option_chain()

    