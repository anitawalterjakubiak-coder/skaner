"""Porownanie cen z Alpaca (IEX) z lista IV / entry points (newsletter, pazdziernik). Uzycie: python3 -I lista_iv.py"""
import json, subprocess
L = {  # ticker: (IV nizsze, [entry points])
"AAPL":(251,[245,219,195]),"AMZN":(199,[226,199,175,151]),"ASML":(1338,[1274,1110,931]),
"AVGO":(422,[365,326,288,251]),"AZO":(3714,[3282,3004,2897,2729]),"BABA":(229,[140,123,103,95]),
"BKNG":(188,[185,165,150,127]),"CELH":(40.6,[37,32,27]),"CPRT":(45.8,[42,37,29,26]),
"CRM":(259,[229,212,193,164]),"CRWD":(108,[100,93,85,75]),"DPZ":(428,[369,332,285]),
"FTNT":(143,[121,109,91]),"HCA":(423,[417,387,356]),"GOOGL":(374,[328,295,274,243]),
"ICE":(172,[162,152,143,124]),"LIN":(496,[487,465,441,413]),"LMT":(500,[509,411,366,319]),
"MA":(529,[527,500,464,428]),"MELI":(2284,[2050,1834,1645,1481]),"META":(906,[686,643,580,532,481]),
"MSFT":(570,[466,419,395,356]),"MSCI":(491,[482,457,438,385]),"MSI":(439,[430,405,387,358]),
"NFLX":(81,[75,70,67,58]),"NKE":(78,[57,52,41]),"NVDA":(321,[198,168,153,130,90]),
"NOW":(204,[135,121,105,80]),"PANW":(213,[200,165,142]),"PLTR":(141,[141,125,105]),
"SPGI":(510,[479,457,429]),"TMO":(554,[528,501,458,414]),"UNH":(437,[409,384,356]),
"V":(335,[325,308,292]),"VEEV":(253,[217,201,169,150]),"WM":(230,[222,213,199]),
"NDAQ":(98,[92,83,77]),"TSM":(None,[282,232,191,134]),"CMG":(44,[]),
}
syms=",".join(L)
sn=json.loads(subprocess.check_output(["curl","-sS","-m","30",f"https://data.alpaca.markets/v2/stocks/snapshots?symbols={syms}&feed=iex"]))
rows=[]
for t,(iv,ep) in L.items():
    s=sn.get(t)
    if not s: rows.append((9e9,f"{t:6} brak danych IEX")); continue
    p=s["latestTrade"]["p"]
    below=[e for e in ep if e>=p]; nxt=min(ep,key=lambda e:abs(e-p)) if ep else None
    hit=max([i+1 for i,e in enumerate(ep) if p<=e],default=0)
    d=((nxt/p-1)*100) if nxt else 0
    ivs=f"{(p/iv-1)*100:+6.0f}%" if iv else "   n/a"
    rows.append((abs(d) if ep else 5e8, f"{t:6}{p:10.2f}  IV {iv if iv else '-':>6}  cena vs IV {ivs}  EP1 {ep[0] if ep else '-':>5}  osiagniete EP: {hit}/{len(ep)}  do najblizszego EP {d:+6.1f}%"))
for _,r in sorted(rows): print(r)
