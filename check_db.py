import sqlite3

conn = sqlite3.connect("market_data/market_data.db")

cur = conn.cursor()

cur.execute("SELECT * FROM spot_candles LIMIT 5")

print(cur.fetchall())

conn.close()