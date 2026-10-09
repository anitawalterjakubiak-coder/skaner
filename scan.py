"""Skaner watchlisty USA: dane Alpaca (IEX). Uzycie: python3 -I scan.py TICKER1 TICKER2 ..."""
import json, subprocess, sys
from datetime import date, timedelta

syms = [s.upper() for s in sys.argv[1:]] or ["CMG", "NFLX", "GOOGL"]

def get(url):
    return json.loads(subprocess.check_output(["curl", "-sS", "-m", "30", url]))

def rsi(c, n=14):
    g = [max(c[i] - c[i-1], 0) for i in range(1, len(c))]
    l = [max(c[i-1] - c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    for i in range(n, len(g)):
        ag, al = (ag * (n-1) + g[i]) / n, (al * (n-1) + l[i]) / n
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

q = ",".join(syms)
start = (date.today() - timedelta(days=75)).isoformat()
snap = get(f"https://data.alpaca.markets/v2/stocks/snapshots?symbols={q}&feed=iex")
bars = get(f"https://data.alpaca.markets/v2/stocks/bars?symbols={q}&timeframe=1Day&limit=10000&adjustment=split&feed=iex&start={start}")["bars"]

rows = []
for s in syms:
    if s not in snap or s not in bars:
        rows.append((s, None)); continue
    b = bars[s]; c = [x["c"] for x in b]; v = [x["v"] for x in b]
    sn = snap[s]; last = sn["latestTrade"]["p"]; pc = sn["prevDailyBar"]["c"]
    avg = sum(v[-21:-1]) / 20
    rows.append((s, dict(last=last, chg=(last/pc-1)*100, rsi=rsi(c), vr=v[-1]/avg,
                         hi=max(x["h"] for x in b[-20:]), lo=min(x["l"] for x in b[-20:]),
                         t=sn["latestTrade"]["t"][:16])))

print(f"{'TICKER':7}{'CENA':>9}{'ZMIANA%':>9}{'RSI14':>7}{'VOL/sr20':>9}{'POZ.20d':>9}  OSTATNIA TRANSAKCJA (UTC)")
for s, r in rows:
    if r is None: print(f"{s:7} brak danych"); continue
    pos = (r['last']-r['lo'])/(r['hi']-r['lo'])*100 if r['hi'] > r['lo'] else 50
    print(f"{s:7}{r['last']:9.2f}{r['chg']:+9.2f}{r['rsi']:7.1f}{r['vr']:9.2f}{pos:8.0f}%  {r['t']}")
