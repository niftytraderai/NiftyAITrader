# ==========================
# NIFTY AI TRADER SETTINGS
# ==========================

# Account
INITIAL_BALANCE = 100000

# Trading Mode
# INDEX / FUTURES / OPTIONS
TRADING_MODE = "OPTIONS"

# Risk Management
STOP_LOSS = 0.005      # 0.5%
TARGET = 0.01          # 1%

MAX_TRADES_PER_DAY = 5
MAX_DAILY_LOSS = 500

# Time Settings
CHECK_INTERVAL = 60  # 1 Minute

# Market Time
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"

# Telegram
SEND_TELEGRAM = True

# Backtesting
BACKTEST_MODE = "OPTIONS"

# ==========================
# AI STRATEGY SETTINGS
# ==========================

AI_SCORE_MIN = 40

CONFIDENCE_MIN = 30

ADX_MIN = 25

RSI_MIN = 55

RSI_MAX = 70

HOLD_OVERNIGHT = True

MAX_HOLD_DAYS = 5