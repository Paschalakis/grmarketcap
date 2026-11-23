import json, os, urllib.request, urllib.error
K=os.environ.get("CMC_API_KEY","")
print("secret present:", bool(K), "len", len(K))
def get(path, key=False):
    base="https://pro-api.coinmarketcap.com" + ("" if key else "/public-api")
    h={"Accept":"application/json"}
    if key: h["X-CMC_PRO_API_KEY"]=K
    try:
        r=urllib.request.urlopen(urllib.request.Request(base+path,headers=h),timeout=30); return r.status, json.load(r)
    except urllib.error.HTTPError as e: return e.code, e.read()[:300]
    except Exception as e: return "ERR", str(e)[:200]
for key in ([False, True] if K else [False]):
    print("\n==== key" if key else "\n==== keyless")
    for p in ["/v1/cryptocurrency/listings/latest?limit=500&convert=EUR","/v3/cryptocurrency/listings/latest?limit=500&convert=EUR","/v1/global-metrics/quotes/latest?convert=EUR","/v3/fear-and-greed/latest","/v1/key/info"]:
        st,j=get(p,key)
        if isinstance(j,dict):
            d=j.get("data"); s=j.get("status",{})
            print(p, st, "credits", s.get("credit_count"), "err", s.get("error_message"))
            if isinstance(d,list): print("   n",len(d)); print("   first", json.dumps(d[0])[:900] if d else "")
            elif isinstance(d,dict): print("   ", json.dumps(d)[:900])
        else: print(p, st, j)
