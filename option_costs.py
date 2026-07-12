BROKERAGE_PER_ORDER = 20

SLIPPAGE_PERCENT = 0.0005

OTHER_CHARGES_PERCENT = 0.0003

def calculate_trade_cost(
    entry_price,
    exit_price,
    quantity
):

    entry_value = entry_price * quantity

    exit_value = exit_price * quantity

    turnover = entry_value + exit_value

    brokerage = BROKERAGE_PER_ORDER * 2

    slippage = turnover * SLIPPAGE_PERCENT

    other_charges = turnover * OTHER_CHARGES_PERCENT

    total_cost = brokerage + slippage + other_charges

    return {
        "brokerage": brokerage,
        "slippage": slippage,
        "other_charges": other_charges,
        "total_cost": total_cost
    }