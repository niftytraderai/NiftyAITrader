import csv
import os

FILE_NAME = "trade_history.csv"


def create_trade_log():

    if os.path.exists(FILE_NAME):
        return

    with open(FILE_NAME, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "Time",
            "Signal",
            "Entry",
            "Exit",
            "Profit",
            "Result",
            "AI_SCORE",
            "RSI",
            "ADX",
            "ATR",
            "EMA20",
            "EMA50",
            "EMA200",
            "PLUS_DI",
            "MINUS_DI",
            "Market_Regime"
        ])


def save_trade(row):

    with open(FILE_NAME, "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(row)