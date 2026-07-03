import csv
import os
from datetime import datetime
from logger import log
from telegram_bot import send_telegram
from datetime import datetime

class PaperTrader:
    def __init__(self):
        self.balance = 100000
        self.position = None
        self.stop_loss = None
        self.target = None
        self.trade_no = 0

    def buy(self, price):
        if self.position is not None:
            log("Already in BUY position")
            return

        self.trade_no += 1
        self.position = price
        self.stop_loss = price * 0.995
        self.target = price * 1.01

        log(f"BUY @ {price:.2f}")
        log(f"Stop Loss : {self.stop_loss:.2f}")
        log(f"Target    : {self.target:.2f}")

        self.log_trade("BUY", price, 0)
        send_telegram(
    f"""🚀 NIFTY AI TRADER

🟢 BUY SIGNAL

📌 Trade No   : #{self.trade_no}
💹 Price      : {price:.2f}
🛑 Stop Loss  : {self.stop_loss:.2f}
🎯 Target     : {self.target:.2f}
💰 Balance    : ₹{self.balance:.2f}
🕒 Time       : {datetime.now().strftime("%H:%M:%S")}

🤖 Version : V4"""
)
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
    f"""🚀 NIFTY AI TRADER

🔴 SELL SIGNAL

📌 Trade No   : #{self.trade_no}
💹 Sell Price : {price:.2f}
💵 Profit     : ₹{profit:.2f}
💰 Balance    : ₹{self.balance:.2f}
🕒 Time       : {datetime.now().strftime("%H:%M:%S")}

🤖 Version : V4"""
)
        self.position = None


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

        if current_price <= self.stop_loss:
            log("STOP LOSS HIT")
            self.sell(current_price)

        elif current_price >= self.target:
            log("TARGET HIT")
            self.sell(current_price)