import sqlite3
import os

DB_PATH = os.path.join("market_data", "market_data.db")


def get_connection():
    os.makedirs("market_data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS spot_candles (

        datetime TEXT PRIMARY KEY,

        open REAL,
        high REAL,
        low REAL,
        close REAL,

        volume REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS option_candles (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        datetime TEXT,

        instrument_key TEXT,

        trading_symbol TEXT,

        strike REAL,

        option_type TEXT,

        expiry TEXT,

        open REAL,

        high REAL,

        low REAL,

        close REAL,

        volume REAL,

        oi REAL
    )
    """)

    conn.commit()
    conn.close()

def save_spot_candle(data):

    conn = get_connection()
    cur = conn.cursor()

    latest = data.iloc[-1]

    cur.execute("""
        INSERT OR IGNORE INTO spot_candles
        (datetime, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(data.index[-1]),
        float(latest["Open"]),
        float(latest["High"]),
        float(latest["Low"]),
        float(latest["Close"]),
        float(latest["Volume"])
    ))

    conn.commit()
    conn.close()    