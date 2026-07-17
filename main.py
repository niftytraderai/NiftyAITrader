import time
import traceback
from option_chain import get_option_contracts
from historical_contract_resolver import resolve_option_contract
from live_data import get_live_option_price
from indicators import add_indicators, add_htf_trend
from database import create_tables, save_spot_candle
from database import create_tables

from config import CHECK_INTERVAL
from data import get_nifty_data
from strategy import generate_signal
from paper_trade import PaperTrader
from logger import log
from market import is_market_open
from telegram_bot import send_telegram
from datetime import datetime

create_tables()

trader = PaperTrader()

trader = PaperTrader()
contracts = get_option_contracts()
print(f"Loaded {len(contracts)} option contracts.")

last_signal = None

while True:

   # if not is_market_open():
   #     log("Market Closed")
   #     time.sleep(CHECK_INTERVAL)
   #     continue

    try:
        # Data download
        data, close = get_nifty_data()

        # Save latest spot candle
        save_spot_candle(data)

        # Indicators
        data = add_indicators(data)

        # HTF Trend
        data = add_htf_trend(data)

        # Signal
        data = generate_signal(data, close)

        signal = data["Signal"].iloc[-1]
        price = float(close.iloc[-1])
        signal_time = data.index[-1]

        signal_side = None

        if signal == "BUY":
            signal_side = "BUY_ENTRY"

        elif signal == "SELL":
            signal_side = "SELL_ENTRY"

        else:
            signal_side = None

        if signal_side is not None:

            contract = resolve_option_contract(
                signal_datetime=signal_time,
                spot_price=price,
                signal_side=signal_side,
                contracts_df=contracts,
            )

            print("\n========== OPTION CONTRACT ==========")
            print(contract)

            option_price = get_live_option_price(
                contract["instrument_key"]
            )

            print(f"OPTION LTP : {option_price}")

        log(f"Signal: {signal}")
        log(f"Price : {price:.2f}")

        if signal in ["BUY", "SELL"] and signal != last_signal:
            send_telegram(
        f"""📊 NIFTY AI SIGNAL

        Signal : {signal}

        Price : {price:.2f}

        Time : {time.strftime("%H:%M:%S")}
        """
            )

            last_signal = signal

        # Cooldown check
        if trader.cooldown_until is not None:
            if datetime.now() < trader.cooldown_until:
                log(
                    f"Cooldown Active until "
                    f"{trader.cooldown_until.strftime('%H:%M:%S')}"
                )
                time.sleep(CHECK_INTERVAL)
                continue

        # Same candle check
        current_candle = datetime.now().replace(second=0, microsecond=0)

        if trader.last_trade_candle == current_candle:
            log("Same candle - Entry skipped")
            time.sleep(CHECK_INTERVAL)
            continue

        # Check exit using LIVE option premium
        if trader.position is not None:

            option_price = get_live_option_price(
                trader.instrument_key
            )

            trader.check_exit(option_price)

            if trader.cooldown_until is not None:
                if datetime.now() < trader.cooldown_until:
                    log("Exit completed - skipping new entry")
                    time.sleep(CHECK_INTERVAL)
                    continue
        if signal == "BUY":
            if trader.position is None:
                trader.buy(
                    option_price,
                    contract["lot_size"],
                    contract["trading_symbol"],
                    price,
                    contract["instrument_key"]
                )
            else:
                log("BUY ignored - Position already open")

        elif signal == "SELL":
            if trader.position is None:

                trader.buy(
                    option_price,
                    contract["lot_size"],
                    contract["trading_symbol"],
                    price,
                    contract["instrument_key"]
                )

            else:
                log("SELL ignored - Position already open")

        else:
            log("No Trade - HOLD")

    except Exception as e:
        log(f"Error: {e}")
        log(traceback.format_exc())

    trader.show_summary()

    log(f"Next check after {CHECK_INTERVAL} seconds...")
    time.sleep(CHECK_INTERVAL)