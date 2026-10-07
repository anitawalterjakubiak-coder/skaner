TICKERS = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
INTERVALS = {"1m": "7d", "5m": "60d", "15m": "60d", "1h": "730d"}
PIVOT_LEN = 5
RR = 2.0
MAX_BARS = 50
COST_R = 0.05def bullish_signals(df, length):
    high, low, close = df["High"].values, df["Low"].values, df["Close"].values
    last_high = last_low = None
    high_broken = low_broken = False
    trend = 0
    out = []
    for i in range(len(df)):
        p = i - length
        if p >= length:
            if high[p] == high[p - length:p + length + 1].max():
                last_high, high_broken = high[p], False
            if low[p] == low[p - length:p + length + 1].min():
                last_low, low_broken = low[p], False
        if last_high is not None and not high_broken and close[i] > last_high:
            high_broken = True
            if last_low is not None:
                out.append((i, "CHoCH" if trend == -1 else "BOS", last_low))
            trend = 1
        if last_low is not None and not low_broken and close[i] < last_low:
            low_broken = True
            trend = -1
    return out


def simulate(df, signals):
    o, h, l, c = (df[k].values for k in ["Open", "High", "Low", "Close"])
    trades = []
    busy_until = -1
    for i, kind, stop in signals:
        if i + 1 >= len(df) or i <= busy_until:
            continue
        entry = o[i + 1]
        risk = entry - stop
        if risk <= 0 or risk / entry > 0.05:
            continue
        target = entry + RR * risk
        result, exit_idx = None, None
        for j in range(i + 1, min(i + 1 + MAX_BARS, len(df))):
            if l[j] <= stop:
                result, exit_idx = -1.0, j
                break
            if h[j] >= target:
                result, exit_idx = RR, j
                break
        if result is None:
            exit_idx = min(i + MAX_BARS, len(df) - 1)
            result = (c[exit_idx] - entry) / risk
        trades.append({"kind": kind, "r": result - COST_R})
        busy_until = exit_idx
    return trades


def stats(trades):
    if not trades:
        return None
    r = pd.Series([t["r"] for t in trades])
    equity = r.cumsum()
    drawdown = (equity.cummax() - equity).max()
    return {
        "transakcje": len(r),
        "% zyskownych": round((r > 0).mean() * 100, 1),
        "srednio R": round(r.mean(), 3),
        "suma R": round(r.sum(), 1),
        "max spadek (R)": round(drawdown, 1),
    }


def load(ticker, interval, period):
    df = yf.download(ticker, period=period, interval=interval,
                     progress=False, auto_adjust=False)
    if df is None or df.empty:
        return None
    if df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    return df.dropna()


if __name__ == "__main__":
    rows = []
    for interval, period in INTERVALS.items():
        all_trades = []
        for t in TICKERS:
            df = load(t, interval, period)
            if df is None or len(df) < PIVOT_LEN * 4:
                continue
            tr = simulate(df, bullish_signals(df, PIVOT_LEN))
            all_trades += tr
            s = stats(tr)
            if s:
                rows.append({"interwal": interval, "spolka": t, **s})
        s = stats(all_trades)
        if s:
            rows.append({"interwal": interval, "spolka": "RAZEM", **s})

    result = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(result.to_string(index=False))
    result.to_csv("wyniki_backtestu.csv", index=False)
    print("\nUwaga: srednio R ponizej 0 oznacza, ze strategia traciła na tych danych.")
