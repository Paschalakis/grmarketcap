import json, os, urllib.request
K=os.environ["CMC_API_KEY"]
def get(path):
    r=urllib.request.urlopen(urllib.request.Request("https://pro-api.coinmarketcap.com"+path,headers={"X-CMC_PRO_API_KEY":K,"Accept":"application/json"}),timeout=30)
    return r.status, json.load(r)
out=["# Real CoinMarketCap API calls (sample)","","Captured from GitHub Actions with the project's key (the key is sent as the `X-CMC_PRO_API_KEY` header and is never stored in this repository).",""]
for path,cut in [("/v1/cryptocurrency/listings/latest?start=1&limit=2&convert=USD&sort=market_cap",None),("/v1/global-metrics/quotes/latest?convert=USD",None),("/v3/fear-and-greed/historical?limit=2",None),("/v1/key/info",None)]:
    st,j=get(path)
    if path.startswith("/v1/key/info"):
        d=j.get("data",{}); j={"status":j.get("status"),"data":{"plan":d.get("plan"),"usage":{"current_month":(d.get("usage") or {}).get("current_month")}}}
    out+=["## `GET "+path+"`","","HTTP "+str(st),"","```json",json.dumps(j,indent=2,ensure_ascii=False)[:6000],"```",""]
open("probe/cmc-sample.md","w").write("\n".join(out))
print("\n".join(out)[:2500])
