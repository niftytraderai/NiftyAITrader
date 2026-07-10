from option_chain import get_option_contracts
from option_selector import (
    get_atm_strike,
    find_option_contract
)

# Option contracts fetch karo
response = get_option_contracts()

# Dictionary me convert karo
contracts = response.to_dict()["data"]

# Current spot price (abhi test ke liye)
spot = 23962.8

atm = get_atm_strike(spot)

print("ATM Strike:", atm)

ce = find_option_contract(
    contracts,
    atm,
    "CE"
)

pe = find_option_contract(
    contracts,
    atm,
    "PE"
)

print("\nATM CE")
print(ce)

print("\nATM PE")
print(pe)