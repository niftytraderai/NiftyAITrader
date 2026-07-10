from option_selector import get_atm_strike
from option_selector import choose_option

spot = 23962.80

atm = get_atm_strike(spot)

print("Spot :", spot)
print("ATM Strike :", atm)
print(choose_option("BUY", atm))
print(choose_option("SELL", atm))