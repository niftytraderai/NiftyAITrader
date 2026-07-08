import requests


def get_option_chain():

    session = requests.Session()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Cookie generate
    session.get(
        "https://www.nseindia.com",
        headers=headers,
        timeout=10
    )

    response = session.get(
        "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    return response.json()

def get_summary():

    data = get_option_chain()

    records = data["records"]["data"]

    total_call = 0
    total_put = 0

    max_call = 0
    max_put = 0

    call_strike = None
    put_strike = None

    for row in records:

        strike = row["strikePrice"]

        if "CE" in row:

            oi = row["CE"]["openInterest"]

            total_call += oi

            if oi > max_call:

                max_call = oi
                call_strike = strike

        if "PE" in row:

            oi = row["PE"]["openInterest"]

            total_put += oi

            if oi > max_put:

                max_put = oi
                put_strike = strike

    pcr = total_put / total_call if total_call else 0

    return {

        "PCR": round(pcr, 2),

        "CALL_OI": total_call,

        "PUT_OI": total_put,

        "MAX_CALL_STRIKE": call_strike,

        "MAX_PUT_STRIKE": put_strike

    }

print("Program Started")

if __name__ == "__main__":

    print("Inside Main")

    result = get_summary()

    print(result)