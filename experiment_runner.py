from backtest import run_backtest

print("\n========== AI EXPERIMENT RUNNER ==========\n")

best_profit = -999999
best_result = None

for ai in [60, 65, 70, 75]:
    for conf in [60, 65, 70, 75]:
        for adx in [20, 25, 30]:
            for rsi_min in [50, 52, 55]:
                for rsi_max in [70, 75, 80]:

                    print(
                        f"Testing "
                        f"AI={ai} "
                        f"CONF={conf} "
                        f"ADX={adx} "
                        f"RSI={rsi_min}-{rsi_max}"
                    )

                    result = run_backtest(
                        ai,
                        conf,
                        adx,
                        rsi_min,
                        rsi_max
                    )

                    if result["profit"] > best_profit:

                        best_profit = result["profit"]

                        best_result = {
                            "AI": ai,
                            "CONF": conf,
                            "ADX": adx,
                            "RSI_MIN": rsi_min,
                            "RSI_MAX": rsi_max,
                            **result
                        }

print("\n=========== BEST SETTINGS ===========\n")

for k, v in best_result.items():
    print(f"{k} : {v}")