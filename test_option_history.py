from option_history import get_option_history_df

df = get_option_history_df("NSE_FO|57338")

print(df.head())

print(df.tail())