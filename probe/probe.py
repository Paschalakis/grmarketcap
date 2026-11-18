import requests, json, time
U="https://api.hyperliquid.xyz/info"
def post(b): r=requests.post(U,json=b,timeout=30); return r.status_code, r.json()
# find an active trader address from recent trades on a liquid coin
c,t=post({"type":"recentTrades","coin":"BTC"}) if False else (0,None)
addrs=["0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"]
try:
    c,lb=post({"type":"vaultSummaries"}); print("vaults",c,str(lb)[:200])
except Exception as e: print("vs err",e)
for a in addrs:
    c,s=post({"type":"spotClearinghouseState","user":a}); print("SPOT",c,json.dumps(s)[:900])
    c,o=post({"type":"frontendOpenOrders","user":a}); print("ORDERS",c,len(o) if isinstance(o,list) else o, json.dumps(o[:2] if isinstance(o,list) else o)[:900])
    st=int(time.time()*1000)-30*86400000
    c,f=post({"type":"userFunding","user":a,"startTime":st}); print("FUNDING",c,len(f) if isinstance(f,list) else f, json.dumps(f[:2] if isinstance(f,list) else f)[:700])
    c,p=post({"type":"portfolio","user":a}); print("PORTFOLIO",c,[x[0] for x in p] if isinstance(p,list) else p)
    if isinstance(p,list):
        for k,v in p:
            if k in ("allTime","day","perpAllTime"): print(k, {kk:(vv[:3] if isinstance(vv,list) else vv) for kk,vv in v.items()}, "n=",len(v.get("accountValueHistory",[])))
    c,cs=post({"type":"clearinghouseState","user":a}); ps=cs.get("assetPositions",[]); print("CH pos sample",json.dumps(ps[:1])[:700])
c,sm=post({"type":"spotMetaAndAssetCtxs"}); print("SPOTMETA",c,json.dumps(sm[0]["tokens"][:3])[:400], json.dumps(sm[0]["universe"][:3])[:400], json.dumps(sm[1][:2])[:400])
