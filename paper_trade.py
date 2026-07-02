import csv
import os
from datetime import datetime

class PaperTrader:
    def __init__(self):
        self.balance = 100000
        self.position = None
        self.stop_loss = None
        self.target = None

    def buy(self, price):
        if self.position is not None:
            print("Already in BUY position")
            return

        self.position = price
        self.stop_loss = price * 0.995
        self.target = price * 1.01

        print(f"BUY @ {price:.2f}")
        print(f"Stop Loss : {self.stop_loss:.2f}")
        print(f"Target    : {self.target:.2f}")

        self.log_trade("BUY", price, 0)

    def sell(self, price):
        if self.position is None:
            print("No open position")
            return

        profit = price - self.position
        self.balance += profit

        print(f"SELL @ {price:.2f}")
        print(f"Profit  = {profit:.2f}")
        print(f"Balance = {self.balance:.2f}")

        self.log_trade("SELL", price, profit)
        self.position = None

    def log_trade(self, action, price, profit):
        file_exists = os.path.isfile("trades.csv")

        with open("trades.csv", "a", newline="") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["Date", "Action", "Price", "Profit"])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action,
                round(price, 2),
                round(profit, 2)
            ])