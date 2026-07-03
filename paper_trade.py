import csv
import os
from datetime import datetime
from logger import log
from telegram_bot import send_telegram


class PaperTrader:
    def __init__(self):
        self.balance = 100000
        self.position = None
        self.stop_loss = None
        self.target = None
        self.trade_no = 0
        self.trailing_active = False

    def buy(self, price):
        if self.position is not None:
            log("Already in BUY position")
            return

        self.trade_no += 1
        self.position = price
        self.stop_loss = price * 0.995
        self.target = price * 1.01
        self.trailing_active = False

        log(f"BUY @ {price:.2f}")
        log(f"Stop Loss : {self.stop_loss:.2f}")
        log(f"Target    : {self.target:.2f}")

        self.log_trade("BUY", price, 0)

        send_telegram(
f"""
━━━━━━━━━━━━━━━━━━━━
🤖 NIFTY AI TRADER
━━━━━━━━━━━━━━━━━━━━

🟢 BUY SIGNAL

📌 Trade No : #{self.trade_no}
💹 Entry    : {price:.2f}

🛑 Stop Loss : {self.stop_loss:.2f}
🎯 Target    : {self.target:.2f}

💰 Balance : ₹{self.balance:.2f}
🕒 Time    : {datetime.now().strftime("%H:%M:%S")}

🤖 Version : V4

━━━━━━━━━━━━━━━━━━━━
"""
        )

        log("Telegram BUY Alert Sent")

    def sell(self, price):
        if self.position is None:
            log("No open position")
            return

        profit = price - self.position
        self.balance += profit

        log(f"SELL @ {price:.2f}")
        log(f"Profit  = {profit:.2f}")
        log(f"Balance = {self.balance:.2f}")

        self.log_trade("SELL", price, profit)

        send_telegram(
f"""
━━━━━━━━━━━━━━━━━━━━
🤖 NIFTY AI TRADER
━━━━━━━━━━━━━━━━━━━━

🔴 SELL SIGNAL

📌 Trade No : #{self.trade_no}
💹 Exit     : {price:.2f}

💵 Profit   : ₹{profit:.2f}
💰 Balance  : ₹{self.balance:.2f}

🕒 Time     : {datetime.now().strftime("%H:%M:%S")}

🤖 Version : V4

━━━━━━━━━━━━━━━━━━━━
"""
        )

        log("Telegram SELL Alert Sent")

        self.position = None
        self.stop_loss = None
        self.target = None
        self.trailing_active = False

    def log_trade(self, action, price, profit):
        file_exists = os.path.isfile("trades.csv")

        with open("trades.csv", "a", newline="") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["Date", "Action", "Price", "Profit", "Balance"])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action,
                round(price, 2),
                round(profit, 2),
                round(self.balance, 2)
            ])

    def check_exit(self, current_price):
        if self.position is None:
            return

        # Activate trailing stop after 0.5% profit
        if (not self.trailing_active) and current_price >= self.position * 1.005:
            self.trailing_active = True
            self.stop_loss = self.position
            log("Trailing Stop Activated")
            send_telegram("🔒 Trailing Stop Activated")

        # Move stop loss higher as price rises
        if self.trailing_active:
            new_stop = current_price * 0.995

            if new_stop > self.stop_loss:
                self.stop_loss = new_stop
                log(f"Trailing Stop Updated : {self.stop_loss:.2f}")

        # Exit conditions
        if current_price <= self.stop_loss:
            log("STOP LOSS HIT")
            self.sell(current_price)

        elif current_price >= self.target:
            log("TARGET HIT")
            self.sell(current_price)

    def show_summary(self):
        if not os.path.exists("trades.csv"):
            log("No trades found.")
            return

        with open("trades.csv", "r") as file:
            reader = csv.DictReader(file)

            total_trades = 0
            wins = 0
            losses = 0
            total_profit = 0

            for row in reader:
                if row["Action"] == "SELL":
                    total_trades += 1
                    profit = float(row["Profit"])
                    total_profit += profit

                    if profit > 0:
                        wins += 1
                    elif profit < 0:
                        losses += 1

        win_rate = 0

        if total_trades > 0:
            win_rate = (wins / total_trades) * 100

        log("========== PERFORMANCE ==========")
        log(f"Total Trades : {total_trades}")
        log(f"Wins         : {wins}")
        log(f"Losses       : {losses}")
        log(f"Win Rate     : {win_rate:.2f}%")
        log(f"Net Profit   : ₹{total_profit:.2f}")
        log(f"Balance      : ₹{self.balance:.2f}")