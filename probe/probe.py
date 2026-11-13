import requests, json, time
H={"User-Agent":"Mozilla/5.0 Chrome/124","Accept":"application/json"}
for q in ["layerzero","octaspace","anyone protocol","plasma","monad","based","star atlas","araistotle"]:
    r=requests.get("https://api.coingecko.com/api/v3/search",params={"query":q},headers=H,timeout=30)
    try: coins=r.json().get("coins",[])[:6]
    except Exception: coins=[]; print(q, r.status_code, r.text[:200])
    print("##",q)
    for c in coins: print(json.dumps({k:c.get(k) for k in ["id","name","symbol","market_cap_rank","large"]}))
    time.sleep(3)
ids="layerzero,octaspace,anyone-protocol,plasma,monad,star-atlas"
r=requests.get("https://api.coingecko.com/api/v3/simple/price",params={"ids":ids,"vs_currencies":"usd"},headers=H,timeout=30); print(r.text)
