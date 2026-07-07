import csv
import os

from data import get_nifty_data
from indicators import add_indicators
from strategy import generate_signal

INITIAL_BALANCE = 100000

TRADE_HISTORY_FILE = "trade_history.csv"


def prepare_trade_history():

    if os.path.exists(TRADE_HISTORY_FILE):
        return

    with open(TRADE_HISTORY_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "EntryTime",
            "ExitTime",
            "EntryPrice",
            "ExitPrice",
            "Profit",
            "Result",
            "EMA20",
            "EMA50",
            "EMA200",
            "RSI",
            "ADX",
            "ATR",
            "MACD",
            "MACD_SIGNAL",
            "AI_SCORE"
        ])


def save_trade(row):

    with open(TRADE_HISTORY_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(row)


def run_backtest():

    print("Downloading Historical Data...")

    prepare_trade_history()

    data, close = get_nifty_data()

    data = add_indicators(data)

    data = generate_signal(data, close)

    balance = INITIAL_BALANCE

    position = None

    entry_time = None

    entry_data = None

    stop_loss = None

    target = None

    highest_price = None

    total_trades = 0

    wins = 0

    losses = 0

    net_profit = 0


    for i in range(len(data)):

        signal = data["Signal"].iloc[i]

        price = float(data["Close"].iloc[i])

        atr = float(data["ATR"].iloc[i])

        if atr <= 0:
            continue

        # ======================
        # BUY
        # ======================

        if position is None and signal == "BUY":

            position = price

            entry_time = data.index[i]

            entry_data = data.iloc[i]

            stop_loss = position - (1.5 * atr)

            target = position + (3 * atr)

            highest_price = position

            continue

        if position is None:
            continue

        # ======================
        # TRAILING STOP
        # ======================

        if price > highest_price:

            highest_price = price

        new_stop = highest_price - (1.5 * atr)

        if new_stop > stop_loss:

            stop_loss = new_stop

        if price >= position + atr:

            stop_loss = max(stop_loss, position)

        exit_reason = None

        if price <= stop_loss:

            exit_reason = "STOPLOSS"

        elif price >= target:

            exit_reason = "TARGET"

        elif signal == "SELL":

            exit_reason = "SELL"


        # ======================
        # CLOSE TRADE
        # ======================

        if exit_reason is not None:

            exit_time = data.index[i]

            exit_price = price

            profit = exit_price - position

            balance += profit

            net_profit += profit

            total_trades += 1

            if profit > 0:

                wins += 1

                result = "WIN"

            else:

                losses += 1

                result = "LOSS"

            save_trade([

                entry_time,

                exit_time,

                round(position, 2),

                round(exit_price, 2),

                round(profit, 2),

                result,

                round(float(entry_data["EMA20"]), 2),

                round(float(entry_data["EMA50"]), 2),

                round(float(entry_data["EMA200"]), 2),

                round(float(entry_data["RSI"]), 2),

                round(float(entry_data["ADX"]), 2),

                round(float(entry_data["ATR"]), 2),

                round(float(entry_data["MACD"]), 2),

                round(float(entry_data["MACD_SIGNAL"]), 2),

                round(float(entry_data["AI_SCORE"]), 2)

            ])

            position = None

            entry_time = None

            entry_data = None

            stop_loss = None

            target = None

            highest_price = None 

    print("\n========== BACKTEST REPORT ==========\n")

    print(f"Initial Balance : ₹{INITIAL_BALANCE:.2f}")
    print(f"Final Balance   : ₹{balance:.2f}")
    print(f"Net Profit      : ₹{net_profit:.2f}")

    print(f"\nTotal Trades : {total_trades}")
    print(f"Wins         : {wins}")
    print(f"Losses       : {losses}")

    if total_trades > 0:
        win_rate = (wins / total_trades) * 100
    else:
        win_rate = 0

    print(f"Win Rate     : {win_rate:.2f}%")                   


if __name__ == "__main__":
    run_backtest()