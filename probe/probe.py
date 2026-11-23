import json, os, urllib.request, urllib.error
K=os.environ["CMC_API_KEY"]
def get(path):
    try:
        r=urllib.request.urlopen(urllib.request.Request("https://pro-api.coinmarketcap.com"+path,headers={"X-CMC_PRO_API_KEY":K,"Accept":"application/json"}),timeout=30)
        return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}
for p in ["/v5/cmc-ai/latest","/v5/cmc-ai/coins/latest?id=1","/v5/cmc-ai/coins/latest?symbol=BTC","/v5/cmc-ai/coins/latest?id=1027,5426",
          "/v1/cryptocurrency/trending/gainers-losers?limit=10&convert=USD&time_period=24h","/v1/cryptocurrency/trending/latest?limit=10&convert=USD",
          "/v1/cryptocurrency/trending/most-visited?limit=10","/v1/cryptocurrency/categories?limit=5","/v1/community/trending/token","/v1/cryptocurrency/listings/latest?limit=1&aux=tags"]:
    st,j=get(p); s=j.get("status",{}) if isinstance(j,dict) else {}
    print("\n###",p,st,"credits",s.get("credit_count"),"err",s.get("error_code"),s.get("error_message"))
    if st==200: print(json.dumps(j.get("data"),ensure_ascii=False)[:1800])
