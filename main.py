import time
import traceback

from config import CHECK_INTERVAL
from data import get_nifty_data
from strategy import generate_signal
from paper_trade import PaperTrader
from logger import log
from market import is_market_open
from telegram_bot import send_telegram

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

        send_telegram(
        f"""📊 NIFTY AI SIGNAL 


        Signal : {signal}

        Price : {price:.2f}

        Time : {time.strftime("%H:%M:%S")}
        """
        )

        trader.check_exit(price)

        if signal == "BUY":
            trader.buy(price)

        elif signal == "SELL":
            trader.sell(price)

        else:
            log("No Trade - HOLD")

    except Exception as e:
        log(f"Error: {e}")
        log(traceback.format_exc())

    trader.show_summary()

    log(f"Next check after {CHECK_INTERVAL} seconds...")
    time.sleep(CHECK_INTERVAL)