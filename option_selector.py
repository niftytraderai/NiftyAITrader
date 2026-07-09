def get_atm_strike(spot_price):

    strike_gap = 50

    atm = round(spot_price / strike_gap) * strike_gap

    return int(atm)

def choose_option(signal, atm):

    if signal == "BUY":
        return f"NIFTY {atm} CE"

    elif signal == "SELL":
        return f"NIFTY {atm} PE"

    return None 

def find_option_contract(contracts, strike, option_type):

    for contract in contracts:

        if (
            contract["strike_price"] == strike
            and contract["instrument_type"] == option_type
        ):

            return {
                "instrument_key": contract["instrument_key"],
                "trading_symbol": contract["trading_symbol"],
                "expiry": contract["expiry"],
                "lot_size": contract["lot_size"]
            }

    return None       