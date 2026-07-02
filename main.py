import time

from config import CHECK_INTERVAL
from data import get_nifty_data
from strategy import generate_signal
from paper_trade import PaperTrader
from logger import log
from market import is_market_open

trader = PaperTrader()

while True:

   # if not is_market_open():
   #     log("Market Closed")
   #     time.sleep(CHECK_INTERVAL)
   #     continue

    try:
        # Data download
        data, close = get_nifty_data()

        # Signal generate
        data = generate_signal(data, close)

        signal = data["Signal"].iloc[-1]
        price = float(close.iloc[-1])

        log(f"Signal: {signal}")
        log(f"Price : {price:.2f}")

        if signal == "BUY":
            trader.buy(price)

        elif signal == "SELL":
            trader.sell(price)

        else:
            log("No Trade - HOLD")

    except Exception as e:
        log(f"Error: {e}")

    log(f"Next check after {CHECK_INTERVAL} seconds...")
    time.sleep(CHECK_INTERVAL)